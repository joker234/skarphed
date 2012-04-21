<?php
###########################################################
# Copyright 2011 Daniel 'grindhold' Brendle and Team
#
# This file is part of Scoville.
#
# Scoville is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later 
# version.
#
# Scoville is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public 
# License along with Scoville. 
# If not, see http://www.gnu.org/licenses/.
###########################################################
namespace scv;

include_once 'core.php';

class DatabaseException extends \Exception {}

class Database {
	private $connection = null;
	
	private $ip = null;
	private $dbname = null;
	private $user = null;
	private $password = null;
	
	private $queryCache = array();
	private $queryRating = array();
	
	public function __construct(){
		$config = Core::getInstance()->getConfig();
		assert($config->getConfigState() == Config::CONF_LOAD_LOCAL);
		$this->setIp($config->getEntry('db.ip'));
		$this->setDbName($config->getEntry('db.name'));
		$this->setUser($config->getEntry('db.user'));
		$this->setPassword($config->getEntry('db.password'));
		$this->connect();
	}
	
	public function setIp ($ip){
		if (preg_match("/\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/",$ip)){
			$this->ip = $ip;
		}else{
			throw new DatabaseException('IP is not valid: '.$ip);
		}
	}
	
	public function setDbName ($dbname){
	    $this->dbname = $dbname;	
	}
	
	public function setUser ($user){
		$this->user = $user;
	}
	
	public function setPassword($pw){
		$this->password = $pw; 
	}
	
	public function connect() {
		if ($this->user == null or $this->ip == null or $this->dbname == null or $this->password == null){
			throw new DatabaseException ('The Parameters for Connection have not been set');
		}
		$connectionstring = $this->ip.":/var/lib/firebird/2.5/data/".$this->dbname;
		$this->connection = ibase_connect($connectionstring,$this->user,$this->password,'UTF8'); 
		if (!$this->connection){
			throw new DatabaseException ('Could not connect to Database due to: '.ibase_errmsg());
		}
		return;
	}
	
	private function getLowestUseQuery(){
		$firstloop = true;
		$lowest = null;
		$lstatement  = null;
		foreach ($this->queryRating as $statement => $rating){
			if ($firstloop){
				$lowest = $rating;
				$lstatement = $statement;
			}else{
				if($rating < $lowest){
					$lowest = $rating;
					$lstatement = $statement;
				}
			}
		}
		return $lstatement;
	}
	
	//HERE BE DRAGONS
	//TODO: Bessere loesung finden
	private function generateZeros($nr){
		$return = "";
		while($nr--!=0){
			$return.="0";
		}
		return $return;
	}
	
	private function replaceModuleTables($module, $statement){
        //Vorhandene Tabellennamen bestimmen und aus der Datenbank holen
		$tagpattern = '/\$\{[A-Za-z]+\}/';
		$matches = array();
		$matchesRaw = array();
		$tablenames = array();
		preg_match_all($tagpattern,$statement,$matches);
		
		foreach ($matches[0] as $match){
			$matchesRaw[] = $match;
		}
		$matchesRaw = array_unique($matchesRaw);
		foreach($matchesRaw as $match){
			$tablename = substr($match,2,strlen($match)-3); 
			$tablenames[] = $tablename;
		}
		
		//TODO: Verhalten implementieren, wenn Tabellen von anderen Modulen mit angesprochen werden.
		$tableqry = "SELECT MDT_ID, MDT_NAME 
		             FROM MODULETABLES 
		              INNER JOIN MODULES ON (MDT_MOD_ID = MOD_ID )
		             WHERE MOD_NAME = ? 
		              AND MDT_NAME IN (?) ;";
        $prepared = ibase_prepare($tableqry);
		$cursor = ibase_execute($prepared,$module->getName(),"'".join("','",$tablenames)."'");
		
		//Tabellennamen ersetzen
		$replacementsDone = array();
		while($nameset = ibase_fetch_object($cursor)){
			$pattern = '/\$\{'.$nameset->MDT_NAME.'\}/';
			$tableId = (string)$nameset->MDT_ID;
			$tableId = "TAB_".$this->generateZeros(6-strlen($tableId)).$tableId; // Entfernen von ${}
			preg_replace($pattern, $tableId, $statement);
			$replacementsDone[] = $nameset->MDT_NAME;
		}
		
		//Errorhandling falls Replacement nicht geklappt hat
		if (count($replacementsDone) != count($matchesRaw)){
			$errorResult = array();
			foreach($matches as $match){
				if (!in_array($match,$replacementsDone)){
					$errorResult[]=$match;
				}
			}
			throw new DatabaseException('Could not resolve Tablenames for: '.join(",",$errorResult));
		}
		return $statement;
	}
	
	private function createQueryInCache($statement){
		if (count($this->queryCache)>20){
			$oldstmnt = $this->getLowestUseQuery();
			unset($this->queryCache[$oldstmnt]);
			unset($this->queryRating[$oldstmnt]);
		}
		$this->queryCache[$statement] = ibase_prepare($statement);
		$this->queryRating[$statement] = 0;
		return $this->queryCache[$statement];
	}
	
	public function getConnection(){
		return $this->connection;
	}
	
	public function query($module, $statement, $args=array(), $forceNoCache=false){
		if(!$this->connection){
			throw new DatabaseException('Database is not Connected');
		}
		if ($module->getName() != 'de.masterprogs.scoville.core'){
		  $statement = $this->replaceModuleTables($module, $statement);	
		}
		if (isset($this->queryCache[$statement])){
			$query = $this->queryCache[$statement];
			$this->queryRating[$statement]++;
		}else{
			$query = $this->createQueryInCache($statement);
		}
		
		$prepared = ibase_prepare($statement);
        array_unshift($args,$prepared);
		$resultset = call_user_func_array('ibase_execute',$args);
		if (!$resultset && ibase_errmsg() != ""){
			throw new DatabaseException('Execution failed due to: '.ibase_errmsg());
		}
		return $resultset;
	}

	public function fetchArray($resultset) {
	  return ibase_fetch_assoc($resultset,ibase_text);
	}
	
	public function fetchObject($resultset) {
	  return ibase_fetch_object($resultset);
	}
	
	public function commit(){
		ibase_commit();
	}
	
	public function createTablesForModule($tables, $modId){
		foreach ($tables as $table) {
			$this->createTableForModule($table, $modId);
		}
	}
	
	public function updateTablesForModule($tables, $modId){
		$res = $this->query($core,"SELECT MDT_ID, MDT_NAME FROM MODULETABLES WHERE MDT_MOD_ID = ?",array($modId));
		$existingTables = array();
		while($set = $this->fetchObject($res)){
			$existingTables[] = array("id"=>$set->MDT_ID,"name"=>$set->MDT_NAME);
		}
		foreach ($tables as $table){
			$found = false;
			foreach ($existingTables as $i=>$existingTables){
				if ($existingTable['name'] == $table->name){
					$found = true;
					unset($existingTables[$i]);
				}
			}
			if (!$found){
				$this->createTableForModule($table, $modId);
			}else{
				//TODO: implement changed columns
			}
			
		}
		foreach($existingTables as $existingTable){
			$this->removeTableForModule($existingTable, $modId)
		}
		
	}
	
	/**
	 * This function creates the tables necessary to run a module
	 * by interpreting the objectlist $table
	 */
	
	private function createTableForModule($tables, $modId){
		//TODO: Implement Sequence
		
		$newTableId = $this->getSeqNext("MDT_GEN"); // Generiere TabellenId
		$newTableString = $this->generateZeros(6-strlen((string)$newTableId)).(string)$newTableId; //Mache string im stile '001234'
		$statement = "CREATE TABLE TAB_$newTableString ( MOD_INSTANCE_ID INT ";
		$autoincrement = null;
		foreach($table->columns as $column){
			$statement.=", $column->name $column->type ";
			if(isset($column->primary)) {
				if($column->primary == true) {
					$statement.="primary key ";
				} else {
					if(isset($column->unique)) {
						if($column->unique == true) {
							$statement.="unique ";
						}
					}
				}
			} else {
				if(isset($column->unique)) {
					if($column->unique == true) {
						$statement.="unique ";
					}
				}
			}
			if(isset($column->notnull)) {
				if($column->notnull == true) {
					$statement.="not null ";
				}
			}
			if(isset($column->autoincrement)) {
				if($column->autoincrement == true) {
					if($autoincrement == null) {
						$autoincrement = $column->name;
					}
				}
			}
		}
		$statement.=");";
		$updateModuleTables = ibase_prepare("INSERT INTO MODULETABLES (MDT_ID, MDT_NAME, MDT_MOD_ID ) VALUES ( ?, ?, ?);");
		ibase_execute($updateModuleTables, $newTableId, $table->name, $modId);
		ibase_query($statement);
		if($autoincrement != null) {
			$statement = "CREATE SEQUENCE SEQ_$newTableString;";
			ibase_query($statement);
			$statement = "SET TERM ^ ;
			CREATE TRIGGER TRG_AUTO_$newTableString FOR TAB_$newTableString
			ACTIVE BEFORE INSERT POSITION 0
			AS
				DECLARE VARIABLE tmp DECIMAL(18,0);
			BEGIN
				IF (NEW.$autoincrement IS NULL) THEN
					NEW.$autoincrement = GEN_ID(, 1);
				ELSE BEGIN
					tmp = GEN_ID(SEQ_$newTableString, 0);
					IF (tmp < new.$autoincrement) THEN
						tmp = GEN_ID(SEQ_$newTableString, new.$autoincrement - tmp);
				END
			END^
			SET TERM ; ^";
			ibase_query($statement);
		}
		
		
// 		foreach ($tables as $table){
// 			$newTableId = $this->getSeqNext("MDT_GEN"); // Generiere TabellenId
// 			$newTableString = $this->generateZeros(6-strlen((string)$newTableId)).(string)$newTableId; //Mache string im stile '001234'
// 			$statement = "CREATE TABLE TAB_$newTableString ( MOD_INSTANCE_ID INT ";
// 			$first = false;
// 			foreach($table->columns as $column){				
// 				$statement.=", $column->name $column->type ";
// 			}
// 			$statement.=");";
// 			$updateModuleTables = ibase_prepare("INSERT INTO MODULETABLES (MDT_ID, MDT_NAME, MDT_MOD_ID ) VALUES ( ?, ?, ?);");
// 			ibase_execute($updateModuleTables, $newTableId, $table->name, $modId);
// 			ibase_query($statement);
// 		}
	}
	
	
	/**
	 * This function removes tables for a specific module
	 */
	
	public function removeTableForModule($table, $modId){
		$gettableIds = "SELECT MDT_ID 
						FROM MODULETABLES 
						WHERE MDT_MOD_ID = ? AND MDT_NAME = ?;";
	    $prepared = ibase_prepare($gettableIds);
		$cursor = ibase_execute($prepared, $modId, $table['name']);
		while($tableset = ibase_fetch_object($cursor)){
			$tabId = "TAB_".$this->generateZeros(6-strlen((string)$tableset->MDT_ID)).(string)$tableset->MDT_ID;
			$deletestmnt = "DROP TABLE $tabId ;";
			ibase_query($deletestmnt);
		}
		return;
	}
	
	public function removeTablesForModule($tables, $modId){
		$gettableIds = "SELECT MDT_ID 
						FROM MODULETABLES 
						WHERE MDT_MOD_ID = ? ;";
	    $prepared = ibase_prepare($gettableIds);
		$cursor = ibase_execute($prepared, $modId);
		while($tableset = ibase_fetch_object($cursor)){
			$tabId = "TAB_".$this->generateZeros(6-strlen((string)$tableset->MDT_ID)).(string)$tableset->MDT_ID;
			$deletestmnt = "DROP TABLE $tabId ;";
			ibase_query($deletestmnt);
		}
		return;
	}

	/**
	 * Gets next value for sequence specified by $sequenceId
	 */
	
	public function getSeqNext($sequenceId){
		return ibase_gen_id($sequenceId);
	}
	
	/**
	 * Gets current value for sequence specified by $sequenceId
	 * 
	 * FIX BLUB
	 */
	
	public function getSeqCurrent($sequenceId){
		//TODO: Here Be Dragons! Absichern von sequenceId!!!
		$statement = "SELECT GEN_ID ( $sequenceId , 0) FROM DUAL;";		
		$cursor = ibase_query($statement);
		$row = ibase_fetch_row($cursor);
		return $row[0];
	}
	
	/**
	 * 
	 * Create blob handler from $data for use with insert and update statements
	 * @param binary $data
	 * @return blobid
	 */
	
	public function createBlob($data) {
		$blh = ibase_blob_create($this->connection);
		ibase_blob_add($blh, $data);
		$blobid = ibase_blob_close($blh);
		return $blobid;
	}
		
	//DEBUG: Method for database-configurationinfo
	public function getInfo(){
		echo("<br>"."Name=".$this->dbname."<br>");
		echo("User=".$this->user."<br>");
		echo("Password=".$this->password."<br>");
		echo("IP=".$this->ip."<br>");
		return;
	}
	
}
?>
