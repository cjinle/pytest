#!/usr/bin/env python
## -*- coding: utf-8 -*-

""" CC互娱配置中心API的解析器 """
# author :      asherzhou
# history:      v1.0
# time:          2013-04-01
# desc:          解析来自CC的API的接口，依据每天的版本变更来做状态变更事件池
#
# history:
#
#
#               2013-07-19:
#                   1.LOGDB的的IP变更没有更新到新库里，唯一key的错误（BUG错误处理）。
#               2013-07-26：
#                   1.增加变更通知机制，采用Redis的（pub/sub）
#
#
#
#
""" 下面为代码 """


import json
import time
import string

""" 拉取CC脚本的subprocess的库 """
import subprocess, shlex



""" DBproxy的库 """
import sys
sys.path.append("../modules")
reload(sys) 
sys.setdefaultencoding('utf-8')

from Comm_Logger import FileLogger
from Comm_DBUtil import DBConfInstance
from Comm_Value import str_escape_string

from Comm_MySQLPoolOper import MySQLPoolOper


#dbconf = DBConfInstance.getDBInstance("NewMetadata")
#mysql_new_meta_conn = MySQLPoolOper(dbconf)



class CC_API_XML_Parser:
    def __init__(self,logger = FileLogger("../log/CC_API_Parser.log")):
        #这个日志只支持单进程的
        self.logger = logger
        self.logger.info(">>>>>>>>CC_API_XML_Parser Start")
        
        
        #存储多分布的gamedr的配置
        #   例如：dr1,dr2,dr3... ...
        self.gamedr_dict = {}
        self.gamedr_md5_dict = {}
    """
        获取CC的Area的业务数据分布
        
        input:      app, 
                      Worldid="worldID", 
                      WorldName="中文名称"
        
        
        return:   (AreaMD5,CC_Area_List)
      
                    AreaMD5 :  0250afff7615df29db792fdf0c781743
  
                    CC_Area_Dict {"406":
                            {  "SetName":"hz_406","worldID":"406", "WorldName":"华夏双线56区"  },
                            "407":
                            {  "SetName":"hz_407","worldID":"407", "WorldName":"华夏双线57区"  },
                        }
        
    """
    def getAreaJsonList(self, app, Worldid="worldID", WorldName=""):
        try:
            #获取DR_MODULE_ID的值，因为不同的业务不同的命名方式
            self.logger.info("app=[%s]Worldid=[%s]WorldName=[%s]", app, Worldid, WorldName)
            CC_Worldid =str(Worldid).decode('utf-8').encode('gb2312')
            CC_app = str(app).decode('utf-8').encode('gb2312')
            CC_WorldName = str(WorldName).decode('utf-8').encode('gb2312')
            self.logger.info("CC_app=[%s]CC_WorldName=[%s]",CC_app,CC_WorldName)

            #获取CC的DR接口返回的XML数据
            #/bin/sh getCCAreaList.sh -a="QXZB七雄争霸" -set_cst_col="worldID","中文名称"
            command_line = "/data/MetaData/server/tools/cc/shell/getCCAreaJsonList.sh  -set_cst_col="+CC_Worldid+","+CC_WorldName+" -a="+CC_app
 
            self.logger.info("command_line=[%s]", command_line)
            
            area_json_handle=subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE)
            
            #Communicate() 的读取返回 (stdoutdata,stderrdata)
            area_json = area_json_handle.communicate()[0]
            self.logger.info("area_json=[%s]", area_json)
            
            #解析XML后，填充CC_Area_List
            return self.parseAreaJson(area_json, Worldid, WorldName)
            
        except Exception as e:
            self.logger.error("getAreaJsonList Error Catch A Exception[%s]", e)
            raise Exception("getAreaJsonList Error Catch A Exception ="+str(e))

    """
        获取CC的Logdb的业务数据分布
        
        input:      app, 
                      logdb_module="tlog", 
                      area_cc_set_dict 
        
        return:   (LogdbMD5,CC_logdb_dict)
      
                    AreaMD5 :  0250afff7615df29db792fdf0c781743
  
                    CC_logdb_dict {"1":
                        {   "1-10.178.52.15":{
                                "iStatus":"1","cIDC":"东莞电信大朗AC", "cDataIP":"10.178.52.15", "cCCWorldID":"world_1"
                            ,"iDistrictID":"1"},
                            "1-10.178.52.14":{
                                "iStatus":"1","cIDC":"东莞电信大朗AC", "cDataIP":"10.178.52.14", "cCCWorldID":"world_1"
                             ,"iDistrictID":"1"},
                            "1-10.178.52.14":{
                                "iStatus":"1","cIDC":"东莞电信大朗AC", "cDataIP":"10.178.52.14", "cCCWorldID":"world_1"
                             ,"iDistrictID":"1"},
                        }
                        "2":
                        {   "2-10.186.0.28":{
                                "iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.28", "cCCWorldID":"world_2"
                             ,"iDistrictID":"2"},
                            "2-10.186.0.26":{
                                "iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.26", "cCCWorldID":"world_2"
                             ,"iDistrictID":"2"},
                            "2-10.186.0.17":{
                                "iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2"
                             ,"iDistrictID":"2"},
                        }
        
    """
    def getLogdbJsonList(self, app, logdb_module="tlog", area_ccset_dict={}):
        try:
            #获取DR_MODULE_ID的值，因为不同的业务不同的命名方式
            self.logger.info("app=[%s]logdb_module=[%s]size(area_ccset_dict)=[%d]", app, logdb_module, len(area_ccset_dict))
            
            #如果area_cc_set_dict 为空，则异常
            if len(area_ccset_dict) == 0:
                self.logger.error("len(area_cc_set_dict) is 0 ,Error")
            CC_app = str(app).decode('utf-8').encode('gb2312')
            CC_logdb_module = str(logdb_module)
            self.logger.info("CC_app=[%s]CC_logdb_module=[%s]",CC_app,CC_logdb_module)
            #获取CC的DR接口返回的XML数据
            #/bin/sh getCCAreaList.sh -a="QXZB七雄争霸" -set_cst_col="worldID","中文名称"
                
            command_line = "/data/MetaData/server/tools/cc/shell/getCCModuleLogdbJson.sh  -am="+CC_logdb_module+" -a="+CC_app
 
            self.logger.info("command_line=[%s]", command_line)
            
            logdb_json_handle=subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE)
            
            #Communicate() 的读取返回 (stdoutdata,stderrdata)
            logdb_json = logdb_json_handle.communicate()[0]
            #self.logger.log("logdb_json=[%s]", logdb_json)
            #self.logger.log("area_ccset_dict=[%s]", repr(area_ccset_dict))
            
            #解析XML后，填充CC_Area_List
            return self.parseLogdbJson(logdb_json, area_ccset_dict)
            
        except Exception as  e:
            self.logger.error("getLogdbJsonList Error Catch A Exception[%s]", e)
            raise Exception("getLogdbJsonList Error Catch A Exception ="+str(e))

    """
        获取CC的Gamedr的业务数据分布
        
        input:      app, 
                      gamedr_module="tlog", 
                      area_cc_set_dict 
        
        return:   (GamedrMD5,CC_Gamedr_dict)
      
                    GamedrMD5 :  0250afff7615df29db792fdf0c781743
  
                    CC_Gamedr_dict(树形索引){ "业务ID" --> "大区ID"-->"dr1"-->"大区ID-ip"-->"IP实体内容"}
                    
                    CC_Gamedr_dict {"1":
                                                {"dr1":
                                                        {  "1-10.178.52.15":{
                                                                    "iStatus":"1","cIDC":"东莞电信大朗AC", "cDataIP":"10.178.52.15", "cCCWorldID":"world_1","iDistrictID":"1"},
                                                             "1-10.178.52.14":{
                                                                    "iStatus":"1","cIDC":"东莞电信大朗AC", "cDataIP":"10.178.52.14", "cCCWorldID":"world_1" ,"iDistrictID":"1"}
                                            }}}
    """
    def getGamedrJsonList(self, app, gamedr_module="gamedr", area_ccset_dict={}):
        try:
            
            for gamedr_module_id in str(gamedr_module).split(","):
                
                #获取DR_MODULE_ID的值，因为不同的业务不同的命名方式
                self.logger.info("app=[%s]gamedr_module_id=[%s]gamedr_module=[%s]size(area_ccset_dict)=[%d]", app, gamedr_module_id, gamedr_module, len(area_ccset_dict))
                
                #如果area_cc_set_dict 为空，则异常
                if len(area_ccset_dict) == 0:
                    self.logger.error("len(area_cc_set_dict) is 0 ,Error")
                
                CC_app = str(app).decode('utf-8').encode('gb2312')
                CC_gamedr_module = str(gamedr_module)
                
                #获取CC的DR接口返回的XML数据
                #/bin/sh getCCAreaList.sh -a="QXZB七雄争霸" -set_cst_col="worldID","中文名称"
                    
                command_line = "/data/MetaData/server/tools/cc/shell/getCCModuleLogdbJson.sh  -am="+gamedr_module_id+" -a="+CC_app
     
                self.logger.info("command_line=[%s]", command_line)
                
                gamedr_json_handle=subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE)
                
                #Communicate() 的读取返回 (stdoutdata,stderrdata)
                gamedr_json = gamedr_json_handle.communicate()[0]
                #self.logger.log("gamedr_json=[%s]", gamedr_json)
                #self.logger.log("area_ccset_dict=[%s]", repr(area_ccset_dict))
                self.parseGamedrJson(gamedr_module_id, gamedr_json, area_ccset_dict)
                
            self.logger.info("self.gamedr_md5_dict[%s]gamedr_dict[%s]",repr(self.gamedr_md5_dict), repr(self.gamedr_dict))
            return self.gamedr_md5_dict,self.gamedr_dict
           
        except Exception as  e:
            self.logger.error("getGamedrJsonList Error Catch A Exception[%s]", e)
            raise Exception("getGamedrJsonList Error Catch A Exception ="+str(e))

    """
        Parser GamedrJSON
        
        return:    (self.gamedr_md5_dict, self.gamedr_dict)
    
    """
    def parseGamedrJson(self, gamedr_module_id,  gamedr_json, area_ccset_dict):
        try:
            cc_area = json.loads(gamedr_json)
            GamedrMD5 = cc_area["response"]["header"]["body_summary"]["body_md5"]
            
            area_dict = {}
            self.logger.info("Now gamedr_module_id=[%s]", gamedr_module_id)
            
            #data 返回有问题
            if len(cc_area["response"]["body"]["data"]) < 1:
                return False
            #List
            for item in cc_area["response"]["body"]["data"]:
                item_dict = {}
                #获取大区ID
                if str(item["TopoSet"]) in area_ccset_dict:
                    area =area_ccset_dict[str(item["TopoSet"])]
                    item_dict["iDistrictID"] = area
                    item_dict["iStatus"] =  "0"
                    if str(item["State"]) == "--->运营中[需告警]":
                        item_dict["iStatus"] =  "1"
                    item_dict["cIDC"] = item["IDC"]
                    item_dict["cDataIP"] = item["InnerIP"]
                    item_dict["cDataHost"] = gamedr_module_id
                    item_dict["cCCWorldID"] = item["TopoSet"]
                    area_dict[str(area)+"-"+str(item["InnerIP"])] = item_dict
            #
            #   Dict的变形记录
            #   """ area_dict 变形为 gamedr_dict """
            
            for area in area_ccset_dict.values():
                tempDict = {}
                for key in area_dict:
                    if key.find("-") > 0:
                        if str(key[:key.find("-")]) == str(area):
                            tempDict[key] = area_dict[key]
                if area not in self.gamedr_dict:
                    self.gamedr_dict[area] = {}
                self.gamedr_dict[area][gamedr_module_id] = tempDict
                
            #MD5
            self.gamedr_md5_dict[gamedr_module_id] = GamedrMD5
            self.logger.log("GamedrMD5=[%s]gamedr_module_id=[%s]", GamedrMD5,gamedr_module_id)
        except Exception as e:
            self.logger.error("parseGamedrJson Error [%s]", e)
            return False



    """
        Parser LogdbJSON
        
        return:    (AreaMD5, CC_Logdb_Dict)
    
    """
    def parseLogdbJson(self, area_json, area_ccset_dict):
        try:
            cc_area = json.loads(area_json)
            LogdbMD5 = cc_area["response"]["header"]["body_summary"]["body_md5"]
            CC_Logdb_Dict = {}
            area_dict = {}
            
            #data 返回有问题
            if len(cc_area["response"]["body"]["data"]) < 1:
                LogdbMD5 = ""
                return LogdbMD5,CC_Logdb_Dict
            
            #List
            for item in cc_area["response"]["body"]["data"]:
                item_dict = {}
                #获取大区ID
                if str(item["TopoSet"]) in area_ccset_dict:
                    area = area_ccset_dict[str(item["TopoSet"])]
                    item_dict["iDistrictID"] = area
                    item_dict["iStatus"] =  "0"
                    if str(item["State"]) == "--->运营中[需告警]":
                        item_dict["iStatus"] =  "1"
                    item_dict["cIDC"] = item["IDC"]
                    item_dict["cDataIP"] = item["InnerIP"]
                    item_dict["cCCWorldID"] = item["TopoSet"]
                    area_dict[str(area)+"-"+str(item["InnerIP"])] = item_dict
            #   Dict的变形记录
            #   """ area_dict 变形为 CC_Logdb_Dict """
            for area in area_ccset_dict.values():
                    tempDict = {}
                    for key in area_dict:
                        if key.find("-") > 0:
                            if str(key[:key.find("-")]) == str(area):
                                tempDict[key] = area_dict[key]
                    CC_Logdb_Dict[area] = tempDict
            self.logger.log("LogdbMD5=[%s]CC_Logdb_Dict=[%s]", LogdbMD5, repr(CC_Logdb_Dict))
            return LogdbMD5,CC_Logdb_Dict
        except Exception as e:
            self.logger.error("parseLogdbJson Error [%s]", e)
            LogdbMD5 = ""
            return LogdbMD5,CC_Logdb_Dict

    """
        Parser AreaJSON
        
        return:    (AreaMD5, CC_Area_List)
    
    """
    def parseAreaJson(self, area_json, Worldid="worldID", WorldName="中文名称"):
        cc_area = json.loads(area_json)
        AreaMD5 = cc_area["response"]["header"]["body_summary"]["body_md5"]
        CC_Area_Dict = {}
        self.logger.log("Worldid=%s&WorldName=%s",Worldid, WorldName)
        
        #data 返回有问题
        if len(cc_area["response"]["body"]["data"]) < 1:
            AreaMD5 = ""
            return AreaMD5,CC_Area_Dict
            
        #带名称，我就更新并退出
        for item_key, item_value in cc_area["response"]["body"]["data"].items():
            item_dict = {}
            
            if str(item_value[str(Worldid)]).isdigit() and str(item_value[u'\u4e2d\u6587\u540d\u79f0'])!="NULL":
                item_dict["SetName"] = item_value["SetName"]
                item_dict["WorldName"] = item_value[u'\u4e2d\u6587\u540d\u79f0']
                item_dict["worldID"] = item_value[str(Worldid)]
                #有可能出现1个大区ID中对应两个CC的Set的情况
                #           例如：天天酷跑中的正式一区和预发布服务器都用的是大区ID=1
                #           ---add by asherzhou 20130702
                if str(item_dict["worldID"]) in CC_Area_Dict:
                    CC_Area_Dict[item_dict["worldID"]]["SetName"] = CC_Area_Dict[item_dict["worldID"]]["SetName"]+"||"+item_value["SetName"]
                    CC_Area_Dict[item_dict["worldID"]]["WorldName"] = CC_Area_Dict[item_dict["worldID"]]["WorldName"]+"||"+item_value[u'\u4e2d\u6587\u540d\u79f0']
                else:
                    CC_Area_Dict[item_dict["worldID"]] = item_dict
                
        self.logger.log("AreaMD5=[%s]CC_Area_Dict=[%s]", AreaMD5, repr(CC_Area_Dict))
        
        #如果没有全大区名字，那就需要判断下，是否为空，如果为空，大区名称暂时未获取
        if len(CC_Area_Dict) == 0:
            for item_key, item_value in cc_area["response"]["body"]["data"].items():
                item_dict = {}
                if str(item_value[str(Worldid)]).isdigit() and str(item_value[u'\u4e2d\u6587\u540d\u79f0'])=="NULL":

                    item_dict["SetName"] = item_value["SetName"]
                    item_dict["WorldName"] = "暂未获取"
                    item_dict["worldID"] = item_value[str(Worldid)]
                    #有可能出现1个大区ID中对应两个CC的Set的情况
                    #           例如：天天酷跑中的正式一区和预发布服务器都用的是大区ID=1
                    #           ---add by asherzhou 20130702
                    if str(item_dict["worldID"]) in CC_Area_Dict:
                        CC_Area_Dict[item_dict["worldID"]]["SetName"] = CC_Area_Dict[item_dict["worldID"]]["SetName"]+"||"+item_value["SetName"]
                        CC_Area_Dict[item_dict["worldID"]]["WorldName"] = CC_Area_Dict[item_dict["worldID"]]["WorldName"]+"||"+item_value[u'\u4e2d\u6587\u540d\u79f0']
                    else:
                        CC_Area_Dict[item_dict["worldID"]] = item_dict
            self.logger.log("AreaMD5=[%s]CC_Area_Dict=[%s]", AreaMD5, repr(CC_Area_Dict))
        
        return AreaMD5,CC_Area_Dict


    


class CCWorker:
    def __init__(self, iSerID="4",cAppName="QXZB七雄争霸", cSetName="SetName",  cWorldID="worldID", cWorldName="中文名称", cCCAreaMD5="asdfasd",  cModuleID_logdb="TLOG", cModuleID_dr="gdr", cCCModuleMD5_logdb="xxx", cCCModuleMD5_dr="xxxx",logger = FileLogger("../log/CCWorker.log")):
        self.logger = logger
        self.proxy_meta_datamap = "tcp://10.187.22.150:21401"
        """ 
            Meta 的全局配置数据
                                    想存储在Redis中-------add by asherzhou 20130426
        """
        self._Meta_iSerID =iSerID
        #Meta的大区列表
        # {"1": {  
        #                "iDistrictID":"1", 
        #                "cDistrictName":"电信一区",
        #                "cCCWorldID":"world_1"}
        #           }}
        self._Meta_AreaDict = {}
        self._Meta_AddAreaDict = {}
        self._Meta_DelAreaDict = {}
        self._Meta_AreaMD5 = cCCAreaMD5
        
        self._Meta_LogdbDict = {}
        self._Meta_AddLogdbDict = {}
        self._Meta_ChgLogdbDict = {}
        self._Meta_DelLogdbDict = {}
        self._Meta_ModuleMD5_logdb = cCCModuleMD5_logdb
        
        
        self._Meta_GamedrDict = {}
        self._Meta_AddGamedrDict = {}
        self._Meta_ChgGamedrDict = {}
        self._Meta_DelGamedrDict = {}
        self._Meta_ModuleMD5_gamedr = cCCModuleMD5_dr
        
        """ 
            CC 的全局配置数据
                                    想存储在Redis中-------add by asherzhou 20130426
        """
        self._CC_APP =cAppName
        self._CC_SetName = cSetName
        
        
        self._CC_WorldID = cWorldID
        self._CC_WorldName = cWorldName
        self._CC_AreaMD5 = ""
        
        self._CC_ModuleID_logdb = cModuleID_logdb
        self._CC_ModuleMD5_logdb = ""
        
        self._CC_ModuleID_dr = cModuleID_dr
        self._CC_ModuleMD5_dr = ""
        
        #CC的Parser
        #因为没有多个线程的抢占性的资源，logger可以重用，只要进程未退出
        #
        self._CC_API_Parser = CC_API_XML_Parser(logger=logger)
        """
            结果数据
        
        """
        #CC的大区列表
        self._CC_AreaDict = {}
        #CC的logdb的列表
        self._CC_LogdbDict = {}
        #CC的logdb的列表
        self._CC_GamedrDict = {}
        #大区和CC的set的映射表
        self._MetaArea_District_Dict = {}
    
    """
        大区更新的LOOP 
                
            ---获取最新的MD5 串
            |---if MD5 !=：
                    |---Check 大区分布，是否有增删改
                    |---
    
    """
    def area_task_loop(self ,mysql_new_meta_conn, redis_conn):
        self.logger.info("AreaMD5=[%s]", self._Meta_AreaMD5)
        #获取CC的结果
        result = self._CC_API_Parser.getAreaJsonList(self._CC_APP, Worldid=self._CC_WorldID, WorldName=self._CC_WorldName)
        if result != None:
            self._CC_AreaMD5,self._CC_AreaDict = result
        else:
            self.logger.error("area_task_loop CC API Fault")
            return False
        if self._CC_AreaMD5 != self._Meta_AreaMD5 and self._CC_AreaMD5!="":        
            #获取meta 的Area分布结果
            self.getMetaServiceAreaList(mysql_new_meta_conn)
        
            #判断MD5.不同，需要更新
            #_CC_AreaDict{"406":
            #                            {  "SetName":"hz_406","worldID":"406", "WorldName":"华夏双线56区"  },
            #             "407":
            #                            {  "SetName":"hz_407","worldID":"407", "WorldName":"华夏双线57区"  },
            #                        }
            #_Meta_AddAreaDict{ "406"
            #                           {"iDistrictID":"406","cDistrictName":"华夏双线56区","cCCWorldID":"hz_406"},
            #                   }
            #   
            #
            self.logger.info("len(self._CC_AreaDict)=[%d]len(self._Meta_AreaDict)=[%d]", len(self._CC_AreaDict), len(self._Meta_AreaDict))
            self.logger.info("_CC_AreaMD5=[%s]_Meta_AreaMD5=[%s]",self._CC_AreaMD5, self._Meta_AreaMD5)
            
            # 需要增加的区
            for area_id, area_info in self._CC_AreaDict.items():
                if area_id not in self._Meta_AreaDict.keys():
                    self._Meta_AddAreaDict[area_id] = area_info
            self.logger.info("Need Add Area Size[%d]",len(self._Meta_AddAreaDict))
            # 需要删除的区
            for area_id, area_info in self._Meta_AreaDict.items():
                if area_id not in self._CC_AreaDict.keys():
                    self._Meta_DelAreaDict[area_id] = area_info
            self.logger.info("Need Del Area Size[%d]",len(self._Meta_DelAreaDict))            
            
            #增加Area的Oper
            self.addMetaServiceArea(mysql_new_meta_conn,redis_conn)
            #删除Area的Oper
            self.delMetaServiceArea(mysql_new_meta_conn,redis_conn)
            
            #更新MD5
            self.updateMetaAreaMD5(mysql_new_meta_conn, MD5=self._CC_AreaMD5)
        else:
            self.logger.info("_CC_AreaMD5 == _Meta_AreaMD5=[%s]",self._CC_AreaMD5) 
    
    """ 
        Meta的业务的Logdb的更新的任务loop
    
    """
    def logdb_task_loop(self, mysql_new_meta_conn, mysql_odm_new_conn, redis_conn):
        self.logger.info("_Meta_ModuleMD5_logdb=[%s]", self._Meta_ModuleMD5_logdb)
        #获取当前的Meta Area 分布
        self.getMetaServiceAreaList(mysql_new_meta_conn)
        #获取CC的结果
        result = self._CC_API_Parser.getLogdbJsonList(self._CC_APP, logdb_module=self._CC_ModuleID_logdb, area_ccset_dict=self._MetaArea_District_Dict)
        if result != None:
            self._CC_ModuleMD5_logdb,self._CC_LogdbDict = result
        else:
            self.logger.error("logdb_task_loop CC API Fault")
            return False
        #                            CC_logdb_dict {"1":
        #                        {   "1-10.178.52.15":{
        #                                "iStatus":"1","cIDC":"东莞电信大朗AC", "cDataIP":"10.178.52.15", "cCCWorldID":"world_1"
        #                            ,"iDistrictID":"1"},
        #                   iDistrictID,cDistrictID,cCCWorldID,cDataIP,iStatus
        #采用set对比方案
        if str(self._CC_ModuleMD5_logdb) != str(self._Meta_ModuleMD5_logdb) and self._CC_ModuleMD5_logdb!="" and self._Meta_ModuleMD5_logdb!="":
            #获取meta 的logdb的分布结果
            self.getMetaServiceLogdbList(mysql_new_meta_conn)

            #获取meta 的logdb的分布结果

            #增加logdb的Oper
            #如果_CC_LogdbDict= ｛｝ 也不错
            #我们来做 area set 的交集，差集 来实现增删改操作
            
            set_cc_area = set(self._CC_LogdbDict.keys())
            set_meta_area = set(self._Meta_LogdbDict.keys())
            set_add_area = set_cc_area - set_meta_area
            set_del_area =  set_meta_area - set_cc_area
            set_intersection_area = set_cc_area & set_meta_area
            
            #增加操作(Area)
            for area in set_add_area:
                self.logger.info(" Area[%s] Logdb New Add[%s]",area, repr(self._CC_LogdbDict[area]))
                for logdb_key in self._CC_LogdbDict[area]:
                    #判断是否是ODM上有配置，如果没有配置那么证明是不是开服
                    #       ---add by asherzhou 20130618
                    
                    tlog_path = self.getODMLogdbIPPath(mysql_odm_new_conn,logdb_key)
                    self._Meta_AddLogdbDict[logdb_key] = self._CC_LogdbDict[str(area)][logdb_key]
                    if tlog_path == None or str(tlog_path) == "":
                        self._Meta_AddLogdbDict[logdb_key]["tlog_path"] = ""
                        #默认tlog_path为空，我们默认为新上线为运营
                        self._Meta_AddLogdbDict[logdb_key]["iStatus"] = "0"
                        self._Meta_AddLogdbDict[logdb_key]["cDBName"] = ""
                        self._Meta_AddLogdbDict[logdb_key]["iPort"] = "0"
                        self._Meta_AddLogdbDict[logdb_key]["cDBChar"] = ""
                    else:
                        self._Meta_AddLogdbDict[logdb_key]["tlog_path"] = str(tlog_path)
                        self._Meta_AddLogdbDict[logdb_key]["iStatus"] = "1"                        
                        #获取TLOG的cDBName,iPort,cDBChar
                        patch_res = self.getODMLogdbIPPatch(mysql_odm_new_conn,logdb_key)
                        if patch_res == None or str(patch_res) == "":
                            self._Meta_AddLogdbDict[logdb_key]["cDBName"] = ""
                            self._Meta_AddLogdbDict[logdb_key]["iPort"] = "0"
                            self._Meta_AddLogdbDict[logdb_key]["cDBChar"] = ""
                        else:
                            self._Meta_AddLogdbDict[logdb_key]["cDBName"], self._Meta_AddLogdbDict[logdb_key]["iPort"], self._Meta_AddLogdbDict[logdb_key]["cDBChar"] = patch_res                    
                            if str(self._Meta_AddLogdbDict[logdb_key]["iPort"]) =="":
                                self._Meta_AddLogdbDict[logdb_key]["iPort"] = "0"
                    
            #删除操作(Area)
            for area in set_del_area:
                self.logger.info(" Area[%s] Logdb New Del[%s]",area, repr(self._Meta_LogdbDict[area]))
                for logdb_key in self._Meta_LogdbDict[area]:
                    self._Meta_DelLogdbDict[logdb_key] = self._Meta_LogdbDict[str(area)][logdb_key]            
            #交集操作(Area)
            for area in set_intersection_area:
                #我们来做logdb key的交集，差集 来实现增删改操作
                set_cc_logdb_key = set(self._CC_LogdbDict[area].keys())
                set_meta_logdb_key = set(self._Meta_LogdbDict[area].keys())
                set_add_logdb_key = set_cc_logdb_key - set_meta_logdb_key
                set_del_logdb_key  =  set_meta_logdb_key - set_cc_logdb_key
                
                #对称差集
                set_diff_logdb_key = set_cc_logdb_key ^ set_meta_logdb_key
                
                #单Area多IP的情况
                if len(set_meta_logdb_key) > 1:
                    #增加操作(logdb_key)
                    for logdb_key in set_add_logdb_key:
                        self.logger.info(" Area[%s] Logdb IP New Add[%s]",area, repr(self._CC_LogdbDict[area]))
                        
                        #判断是否是ODM上有配置，如果没有配置那么证明是不是开服
                        #       ---add by asherzhou 20130618                        
                        
                        tlog_path = self.getODMLogdbIPPath(mysql_odm_new_conn,logdb_key)
                        
                        self._Meta_AddLogdbDict[logdb_key] = self._CC_LogdbDict[str(area)][logdb_key]
                        if tlog_path == None or str(tlog_path) == "":
                            self._Meta_AddLogdbDict[logdb_key]["tlog_path"] = ""
                            #默认tlog_path为空，我们默认为新上线未运营
                            self._Meta_AddLogdbDict[logdb_key]["iStatus"] = "0"
                            self._Meta_AddLogdbDict[logdb_key]["cDBName"] = ""
                            self._Meta_AddLogdbDict[logdb_key]["iPort"] = "0"
                            self._Meta_AddLogdbDict[logdb_key]["cDBChar"] = ""
                        else:
                            self._Meta_AddLogdbDict[logdb_key]["tlog_path"] = str(tlog_path)
                            self._Meta_AddLogdbDict[logdb_key]["iStatus"] = "1"   
                            #获取TLOG的cDBName,iPort,cDBChar
                            patch_res = self.getODMLogdbIPPatch(mysql_odm_new_conn,logdb_key)
                            if patch_res == None or str(patch_res) == "":
                                self._Meta_AddLogdbDict[logdb_key]["cDBName"] = ""
                                self._Meta_AddLogdbDict[logdb_key]["iPort"] = "0"
                                self._Meta_AddLogdbDict[logdb_key]["cDBChar"] = ""
                            else:
                                self._Meta_AddLogdbDict[logdb_key]["cDBName"], self._Meta_AddLogdbDict[logdb_key]["iPort"], self._Meta_AddLogdbDict[logdb_key]["cDBChar"] = patch_res
                                if str(self._Meta_AddLogdbDict[logdb_key]["iPort"]) == "":
                                    self._Meta_AddLogdbDict[logdb_key]["iPort"] = "0"
                    #删除操作(logdb_key)
                    for logdb_key in set_del_logdb_key:
                        self.logger.info(" Area[%s] Logdb IP New Del[%s]",area, repr(self._Meta_LogdbDict[area]))
                        self._Meta_DelLogdbDict[logdb_key] = self._Meta_LogdbDict[str(area)][logdb_key]
                
                #单IP和单Area的情况（包含，CC中配置新旧2个IP的情况，比如：XY轩辕传奇出现过）
                if len(set_meta_logdb_key) == 1:
                    #我们有对称差集呵呵，只要，是A,B两个，那么一定是更换
                    if len(set_diff_logdb_key) == 2 and len(set_add_logdb_key) == 1:
                        tmp_dict = {}
                        for chg_logdb_key in set_meta_logdb_key:
                            #iDistrictID,cDistrictID,cCCWorldID,cDataIP,iStatus
                            tmp_dict["cFromDataIP"] = self._Meta_LogdbDict[str(area)][chg_logdb_key]["cDataIP"]
                            #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                            for new_logdb_key in set_add_logdb_key:

                                #判断是否是ODM上有配置，如果没有配置那么证明是不是开服
                                #       ---add by asherzhou 20130618                        
                                
                                tlog_path = self.getODMLogdbIPPath(mysql_odm_new_conn,new_logdb_key)
                                if tlog_path == None or str(tlog_path) == "":
                                    tmp_dict["tlog_path"] = ""
                                    tmp_dict["iStatus"] = "0"
                                    tmp_dict["cDBName"] = ""
                                    tmp_dict["iPort"] = "0"
                                    tmp_dict["cDBChar"] = ""
                                else:
                                    tmp_dict["tlog_path"] = str(tlog_path)
                                    tmp_dict["iStatus"] = "1"
                                    #获取TLOG的cDBName,iPort,cDBChar
                                    patch_res = self.getODMLogdbIPPatch(mysql_odm_new_conn,new_logdb_key)
                                    if patch_res == None or str(patch_res) == "":
                                        tmp_dict["cDBName"] = ""
                                        tmp_dict["iPort"] = "0"
                                        tmp_dict["cDBChar"] = ""
                                    else:
                                        tmp_dict["cDBName"],tmp_dict["iPort"],tmp_dict["cDBChar"] = patch_res
                                        if str(tmp_dict["iPort"]) == "":
                                            tmp_dict["iPort"] = "0"

                                tmp_dict["cToDataIP"] = self._CC_LogdbDict[str(area)][new_logdb_key]["cDataIP"]
                                tmp_dict["cDataIP"] = self._CC_LogdbDict[str(area)][new_logdb_key]["cDataIP"]
                                tmp_dict["cIDC"] = self._CC_LogdbDict[str(area)][new_logdb_key]["cIDC"]
                                tmp_dict["cCCWorldID"] = self._CC_LogdbDict[str(area)][new_logdb_key]["cCCWorldID"]
                                tmp_dict["iDistrictID"] = self._CC_LogdbDict[str(area)][new_logdb_key]["iDistrictID"]
                                
                            self._Meta_ChgLogdbDict[chg_logdb_key] = tmp_dict
                    
                    
                    
                

            self.logger.info("Need Add Logdb Size[%d]",len(self._Meta_AddLogdbDict))
            self.logger.info("Need Del Logdb Size[%d]",len(self._Meta_DelLogdbDict))
            
            #增加logdb的Oper
            self.addMetaServiceLogdb(mysql_new_meta_conn,redis_conn)
            
            #删除logdb的Oper
            self.delMetaServiceLogdb(mysql_new_meta_conn,redis_conn)
            
            #修改logdb的Oper
            self.chgMetaServiceLogdb(mysql_new_meta_conn,redis_conn)
            
            #更新MD5
            self.updateMetaLogdbMD5(mysql_new_meta_conn,MD5=self._CC_ModuleMD5_logdb)
        else:
            self.logger.info("_CC_ModuleMD5_logdb == _Meta_ModuleMD5_logdb=[%s]",self._CC_ModuleMD5_logdb)



    """ 
        Meta的业务的gamedr的更新的任务loop
    
    """
    def gamedr_task_loop(self, mysql_new_meta_conn, redis_conn):
        self.logger.info("_Meta_ModuleMD5_gamedr=[%s]", self._Meta_ModuleMD5_gamedr)
        self._Meta_ModuleMD5_gamedr = self._Meta_ModuleMD5_gamedr.replace("\\\"", "\"")
        try:
            ModuleMD5_gamedr_dict = json.loads(self._Meta_ModuleMD5_gamedr)
            self.logger.info("json loads is correct [%s]", repr(ModuleMD5_gamedr_dict))
            
            #获取当前的Meta Area 分布
            self.getMetaServiceAreaList(mysql_new_meta_conn)
            #获取CC的结果
            result = self._CC_API_Parser.getGamedrJsonList(self._CC_APP, gamedr_module=self._CC_ModuleID_dr, area_ccset_dict=self._MetaArea_District_Dict)
            if result != None:
                self._CC_ModuleMD5_dr,self._CC_GamedrDict = result
            else:
                self.logger.error("gamedr_task_loop CC API Fault")
                return False
            
            self.logger.info("ModuleMD5_gamedr_dict[%s]_CC_ModuleMD5_dr[%s]", repr(ModuleMD5_gamedr_dict), repr(self._CC_ModuleMD5_dr))
            
            #如果MD5不相等说明有变化
            #
            if cmp(self._CC_ModuleMD5_dr, ModuleMD5_gamedr_dict) != 0 and len(self._CC_ModuleMD5_dr)!=0 and len(ModuleMD5_gamedr_dict)!=0:
                #获取meta 的Gamedr的分布结果
                self.getMetaServiceGamedrList(mysql_new_meta_conn)
                
                #增加Gamedr的Oper
                #如果_CC_GamedrDict = ｛｝ 也不错
                
                #我们来做 area set 的交集，差集 来实现增删改操作
                set_cc_area = set(self._CC_GamedrDict.keys())
                set_meta_area = set(self._Meta_GamedrDict.keys())
                set_add_area = set_cc_area - set_meta_area
                set_del_area =  set_meta_area - set_cc_area
                set_intersection_area = set_cc_area & set_meta_area
                
                self.logger.info("Area Set ADD[%s],Del[%s],Intersection[%s]",repr(set_add_area) , repr(set_del_area), repr(set_intersection_area))
                #增加操作(Area)
                for area in set_add_area:
                    self.logger.info(" Area[%s] GameDR New Add[%s]",area, repr(self._CC_GamedrDict[area]))
                    for gamedr_module in self._CC_GamedrDict[area]:
                        for gamedr_key in self._CC_GamedrDict[area][gamedr_module]:
                            self._Meta_AddGamedrDict[gamedr_key] = self._CC_GamedrDict[str(area)][gamedr_module][gamedr_key]
                
                #删除操作(Area)
                for area in set_del_area:
                    self.logger.info(" Area[%s] GameDR New Del[%s]",area, repr(self._Meta_GamedrDict[area]))
                    for gamedr_module in self._Meta_GamedrDict[area]:
                        for gamedr_key in self._Meta_GamedrDict[area][gamedr_module]:
                            self._Meta_DelGamedrDict[gamedr_key] = self._Meta_GamedrDict[str(area)][gamedr_module][gamedr_key]
                
                #交集操作(Area)
                for area in set_intersection_area:
                    
                    #我们来做gamedr key的交集，差集 来实现增删改操作
                    set_cc_gamedr_key = set(self._CC_GamedrDict[area].keys())
                    set_meta_gamedr_key = set(self._Meta_GamedrDict[area].keys())
                    set_add_gamedr_key = set_cc_gamedr_key - set_meta_gamedr_key
                    set_del_gamedr_key  =  set_meta_gamedr_key - set_cc_gamedr_key
                    
                    #对称差集(a^b  在a或者b中，但是不会同时出现在a,b中)
                    set_diff_gamedr_key = set_cc_gamedr_key ^ set_meta_gamedr_key
                    
                    self.logger.info("Area[%s] Gamedr  Set ADD[%s],Del[%s],Intersection[%s]",area, repr(set_add_gamedr_key) , repr(set_del_gamedr_key), repr(set_diff_gamedr_key))
                    
                    
                    #单Area多gamedr IP的情况
                    if len(set_meta_gamedr_key) > 1:
                        #增加操作(gamedr_key)
                        for gamedr_key in set_add_gamedr_key:
                            self.logger.info("Area[%s] Gamedr IP New Add[%s]",area, repr(self._CC_GamedrDict[area]))
                            self._Meta_AddGamedrDict[gamedr_key] = self._CC_GamedrDict[str(area)][gamedr_module][gamedr_key]
                        #删除操作(gamedr_key)
                        for gamedr_key in set_del_gamedr_key:
                            self.logger.info(" Area[%s] Logdb IP New Del[%s]",area, repr(self._Meta_GamedrDict[area]))
                            self._Meta_DelGamedrDict[gamedr_key] = self._Meta_GamedrDict[str(area)][gamedr_key]
                                    
                    #单IP和单Area的情况（包含，CC中配置新旧2个IP的情况，比如：XY轩辕传奇出现过）
                    if len(set_meta_gamedr_key) == 1:
                        #我们有对称差集呵呵，只要，是A,B两个，那么一定是更换
                        if len(set_diff_gamedr_key) == 2 and len(set_add_gamedr_key) == 1: 
                            tmp_dict = {}
                            for chg_gamedr_key in set_meta_gamedr_key:
                                #iDistrictID,cDistrictID,cCCWorldID,cDataIP,iStatus
                                tmp_dict["cFromDataIP"] = self._Meta_GamedrDict[str(area)][chg_gamedr_key]["cDataIP"]
                                #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                                for new_gamedr_key in set_add_gamedr_key:
                                    tmp_dict["cToDataIP"] = self._CC_GamedrDict[str(area)][new_gamedr_key]["cDataIP"]
                                    tmp_dict["cDataIP"] = self._CC_GamedrDict[str(area)][new_gamedr_key]["cDataIP"]
                                    tmp_dict["iStatus"] = self._CC_GamedrDict[str(area)][new_gamedr_key]["iStatus"]
                                    tmp_dict["cIDC"] = self._CC_GamedrDict[str(area)][new_gamedr_key]["cIDC"]
                                    tmp_dict["cCCWorldID"] = self._CC_GamedrDict[str(area)][new_gamedr_key]["cCCWorldID"]
                                    tmp_dict["iDistrictID"] = self._CC_GamedrDict[str(area)][new_gamedr_key]["iDistrictID"]
                            self._Meta_ChgGamedrDict[chg_gamedr_key] = tmp_dict
                            
                #增加gamedr的Oper
                self.addMetaServiceGamedr(mysql_new_meta_conn,redis_conn)
                
                #删除gamedr的Oper
                self.delMetaServiceGamedr(mysql_new_meta_conn,redis_conn)
                
                #修改gamedr的Oper
                self.chgMetaServiceGamedr(mysql_new_meta_conn,redis_conn)
                
                #更新MD5
                self.updateMetaGamedrMD5(mysql_new_meta_conn,MD5=self._CC_ModuleMD5_dr)
        except Exception as e:
            self.logger.error(" gamedr_task_loop Catch A Exception[%s]", e)

    """ 
        查询Logdb的业务Tlog的path的列表
    
    """
    def getODMLogdbIPPath(self,mysql_odm_new_conn, logdb_key):
        
        try:
            #获取logdb_key中的logdb和大区ID
            iDistrictId,logdb_ip = logdb_key.split("-")
            get_sql="select vLogpath from dbODMHealth.tbCfgDB where vIP='"+str(logdb_ip)+"' and iWorldID='"+str(iDistrictId)+"' and vDBType='logtool'"
            
            self.logger.info("getODMLogdbIPPath get_sql=[%s]", get_sql)
            
            res,rows,records = mysql_odm_new_conn.query(get_sql)
            
            self.logger.info("getODMLogdbIPPath rows=[%d]", rows)
            #没有记录
            if rows < 1:
                return None
            elif rows == 1:
                self.logger.info("getODMLogdbIPPath get result vLogpath [%s]",str(records[0]["vLogpath"]))
                return records[0]["vLogpath"]
            else:
                self.logger.error("getODMLogdbIPPath get result size is larger than 1")
                return ""
                
        except Exception as e:
            self.logger.error(" getODMLogdbIPPath Catch A Exception[%s]", e)
            return None

    """ 
        查询Logdb的业务Tlog的port charset dbname的列表
    
    """
    def getODMLogdbIPPatch(self, mysql_odm_new_conn, logdb_key):
        
        try:
            #获取logdb_key中的logdb和大区ID
            iDistrictId,logdb_ip = logdb_key.split("-")
            get_sql="select iPort,vDBName,vCharacterSet from dbODMHealth.tbCfgDB where vIP='"+str(logdb_ip)+"' and iWorldID='"+str(iDistrictId)+"' and vDBType='logdb'"
            
            self.logger.info("getODMLogdbIPPatch get_sql=[%s]", get_sql)
            
            res,rows,records = mysql_odm_new_conn.query(get_sql)
            
            self.logger.info("getODMLogdbIPPatch rows=[%d]", rows)
            #没有记录
            if rows < 1:
                return None
            elif rows == 1:
                self.logger.info("getODMLogdbIPPatch get result iPort [%s] vDBName [%s] vCharacterSet [%s]",str(records[0]["iPort"]),str(records[0]["vDBName"]),str(records[0]["vCharacterSet"]))
                return (str(records[0]["vDBName"]),str(records[0]["iPort"]),str(records[0]["vCharacterSet"]))
            else:
                self.logger.error("getODMLogdbIPPatch get result size is larger than 1")
                return ""
                
        except Exception as e:
            self.logger.error(" getODMLogdbIPPatch Catch A Exception[%s]", e)
            return None
    """ 
        查询META的业务的logdb分布的列表 (((调用DBproxy)))
            a.新增状态的判断，iStatus in (0,1) 
                        ---add by asherzhou 2013702
    
    """
    def getMetaServiceLogdbList(self,mysql_new_meta_conn):
        try:
            get_logdb_list_sql="select iDistrictID,cDistrictID,cCCWorldID,cDataIP,iStatus from db_MetaDataMap.md_data_district where iSerID="+str(self._Meta_iSerID)+" and iDataID=1 and iStatus in (0,1)"
            self.logger.info("get_logdb_list_sql=[%s]", get_logdb_list_sql)
            
            res,rows,records = mysql_new_meta_conn.query(get_logdb_list_sql)
            
            self.logger.info("rows=[%d]len(records)=%d", rows, len(records))
            logdbDict = {}
            for result in records:
                logdbDict[result["cDistrictID"]] = result
            for area in self._MetaArea_District_Dict.values():
                tempDict = {}
                for key in logdbDict:
                    if key.find("-") > 0:
                        if str(key[:key.find("-")]) == str(area):
                            tempDict[key] = logdbDict[key]
                if len(tempDict) != 0:
                    self._Meta_LogdbDict[area] = tempDict
            self.logger.info("self._Meta_LogdbDict =[%s]", repr(self._Meta_LogdbDict))
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("getMetaServiceLogdbList Error Catch A Exception ="+str(e))
    """ 
        查询META的业务的Gamedr分布的列表 (((调用DBproxy)))
    
    """
    def getMetaServiceGamedrList(self,mysql_new_meta_conn):
        try:
            get_gamedr_list_sql="select iDistrictID,cDistrictID,cCCWorldID,cDataIP,cDataHost,iStatus from db_MetaDataMap.md_data_district where iSerID="+str(self._Meta_iSerID)+" and iDataID=2 and iStatus in (0,1)"
            self.logger.info("get_gamedr_list_sql=[%s]", get_gamedr_list_sql)
            
            #b.用链接实例来查询
            res,rows,records = mysql_new_meta_conn.query(get_gamedr_list_sql)
            
            self.logger.info("rows=[%d]len(records)=%d", rows, len(records))
            gamedrDict = {}
            
            #数据封装
            for result in records:
                gamedrDict[result["cDistrictID"]]  = result
            
            #area: {dr1:[{area-ip1:{}},{area-ip2:{}}],
            #            dr2:[{area-ip1:{}},{area-ip2:{}}]}
            #
            gamedr_module_dict = {}
            for area in self._MetaArea_District_Dict.values():
                tempDict = {}
                for dr_key in gamedrDict:
                    if dr_key.find("-") > 0:
                        if str(dr_key[:dr_key.find("-")]) == str(area):
                            if gamedrDict[dr_key]["cDataHost"] not in tempDict:
                                tempDict[gamedrDict[dr_key]["cDataHost"]] = []
                            tempDict[gamedrDict[dr_key]["cDataHost"]].append({dr_key:gamedrDict[dr_key]})
                if len(tempDict) != 0:
                    gamedr_module_dict[area] = tempDict
            #area: {dr1:{area-ip1:{},area-ip2:{}},
            #            dr2:{area-ip1:{}},{area-ip2:{}}}
            #
            for area in gamedr_module_dict:
                tempDrModuleDict ={}
                for dr_module_key in gamedr_module_dict[area]:
                    tempDict = {}
                    for ip_list in gamedr_module_dict[area][dr_module_key]:
                        for area_ip_key in ip_list:
                            tempDict[area_ip_key] = ip_list[area_ip_key]
                    tempDrModuleDict[dr_module_key] = tempDict
                self._Meta_GamedrDict[area] = tempDrModuleDict
            self.logger.info("self._Meta_GamedrList =[%s]", repr(self._Meta_GamedrDict))
        except Exception as e:
            self.logger.error(" getMetaServiceGamedrList Catch A Exception[%s]", e)
            raise Exception("getMetaServiceGamedrList Error Catch A Exception ="+str(e))
    """ 
        查询META的业务的Area的列表 (((调用DBproxy)))
    
    """
    def getMetaServiceAreaList(self,mysql_new_meta_conn):
        try:
            get_area_list_sql="select iDistrictID,cDistrictName,cCCWorldID from db_MetaDataMap.md_service_district where iSerID="+str(self._Meta_iSerID)
            self.logger.info("get_area_list_sql=[%s]", get_area_list_sql)
            
            res,rows,records = mysql_new_meta_conn.query(get_area_list_sql)
            self.logger.info("rows=[%d]len(records)=%d", rows, len(records))
            
            for result in records:
                self._Meta_AreaDict[result["iDistrictID"]] = result
                #因为大区ID可以1对多个CC的SET，所以要加以区分
                #           add by asherzhou 20130702
                if len(str(result["cCCWorldID"]).split("||")) != 1:
                    for ccWorld in str(result["cCCWorldID"]).split("||"):
                        self._MetaArea_District_Dict[ccWorld] = result["iDistrictID"]
                else:
                    self._MetaArea_District_Dict[str(result["cCCWorldID"])] = result["iDistrictID"]
            
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("getMetaServiceAreaList Error Catch A Exception ="+str(e))

    """ 
        增加META的业务的Area的列表 (((调用DBproxy)))
    
    """
    def addMetaServiceArea(self,mysql_new_meta_conn,redis_conn):
        try:
            add_area_list_sql="insert into db_MetaDataMap.md_service_district(iDistrictID,cDistrictName,cCCWorldID,iSerID) values(%s,%s,%s,%s)"
            self.logger.info("add_area_list_sql=[%s]", add_area_list_sql)
            for add_area_id,add_area  in self._Meta_AddAreaDict.items():
                area_add_param =(str(add_area_id), str(add_area["WorldName"]), str(add_area["SetName"]),str(self._Meta_iSerID))
                self.logger.info("id[%s]name[%s]cc_set[%s]serid[%s]", add_area_id, add_area["WorldName"], add_area["SetName"], self._Meta_iSerID)

                res,rows,desc = mysql_new_meta_conn.execute(add_area_list_sql, param=area_add_param)
                self.logger.info("rows=[%d]", rows)
                iDataID = "4"
                iDistrictID = str(add_area_id)
                vOper = "CC配置系统同步"
                iOperType = "11"#大区增加
                iActionType = "1"   #（0:默认动作,1:增加动作,2:修改动作,3:删除动作）'
                vFromValue = ""
                vToValue = str(add_area_id)
                iOperRes = "1"          #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "新开服大区["+str(add_area_id)+"]("+str(add_area["WorldName"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error Insert"
                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn, redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=str(add_area_id), vField2=str(add_area["WorldName"]))

        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaServiceArea Error Catch A Exception ="+str(e))
    
    """ 
        增加META的业务的Logdb的信息 (((调用DBproxy)))
    
    """
    def addMetaServiceLogdb(self,mysql_new_meta_conn,redis_conn):
        try:
            add_logdb_list_sql="insert into db_MetaDataMap.md_data_district(cDistrictID,iSerID,iDataID,cDataIP,cDBName,iPort,cDBChar,cDataHost,iStatus,iDistrictID,cCCWorldID,cIDC,cTlogPath) "
            #并不是所有的新增的IP的状态都是运营状态。
            #       1：logpath为空的，判断为预上线
            #       2：IP的在ODM上没有的，判断为预上线
            #获取TLOG的cDBName,iPort,cDBChar（20130626）
            #       1: cDBName,iPort,cDBChar 加入
            add_logdb_list_sql+=" values(%s,%s,1,%s,%s,%s,%s,'',%s,%s,%s,%s,%s)"
            self.logger.info("add_logdb_list_sql=[%s]", add_logdb_list_sql)
            for add_logdb_key in self._Meta_AddLogdbDict:
                iDistrictID = str(add_logdb_key[:add_logdb_key.find("-")])
                
                #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                add_logdb_param =(add_logdb_key, str(self._Meta_iSerID), str(self._Meta_AddLogdbDict[add_logdb_key]["cDataIP"]),\
                                            str(self._Meta_AddLogdbDict[add_logdb_key]["cDBName"]),\
                                            str(self._Meta_AddLogdbDict[add_logdb_key]["iPort"]),\
                                            str(self._Meta_AddLogdbDict[add_logdb_key]["cDBChar"]),\
                                            str(self._Meta_AddLogdbDict[add_logdb_key]["iStatus"]),iDistrictID, \
                                            str(self._Meta_AddLogdbDict[add_logdb_key]["cCCWorldID"]),\
                                            str(self._Meta_AddLogdbDict[add_logdb_key]["cIDC"]), \
                                            str(self._Meta_AddLogdbDict[add_logdb_key]["tlog_path"]))
                self.logger.info("iDistrictID[%s]cDataIP[%s]cTlogPath[%s]", iDistrictID, str(self._Meta_AddLogdbDict[add_logdb_key]["cDataIP"]), str(self._Meta_AddLogdbDict[add_logdb_key]["tlog_path"]))
                
                res,rows,desc = mysql_new_meta_conn.execute(add_logdb_list_sql, param=add_logdb_param)
                self.logger.info("rows=[%d]", rows)
                
                # 如果logpath为空，那么不需要更新事件
                #           add by asherzhou 20130702
                if str(self._Meta_AddLogdbDict[add_logdb_key]["tlog_path"]) == "":
                    continue
                
                iDataID = "1"
                vOper = "CC配置系统同步"
                iOperType = "31"   #LOGDB的IP增加
                iActionType = "1"   #（0:默认动作,1:增加动作,2:修改动作,3:删除动作）'
                vFromValue = ""
                vToValue = str(self._Meta_AddLogdbDict[add_logdb_key]["cDataIP"])
                iOperRes = "1"          #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "新增加大区["+iDistrictID+"]的Logdb的IP("+str(self._Meta_AddLogdbDict[add_logdb_key]["cDataIP"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error insert"
                
                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn,redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=str(self._Meta_AddLogdbDict[add_logdb_key]["cDataIP"]), vField2=str(self._Meta_AddLogdbDict[add_logdb_key]["tlog_path"]))    
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaServiceLogdb Error Catch A Exception ="+str(e))


    """ 
        修改META的业务的Logdb的信息
    """
    def chgMetaServiceLogdb(self,mysql_new_meta_conn,redis_conn):
        try:
            #先增加
            add_logdb_list_sql="insert into db_MetaDataMap.md_data_district(cDistrictID,iSerID,iDataID,cDataIP,cDBName,iPort,cDBChar,cDataHost,iStatus,iDistrictID,cCCWorldID,cIDC,cTlogPath) "
            add_logdb_list_sql+=" values(%s,%s,1,%s,%s,%s,%s,'',%s,%s,%s,%s,%s)"
            self.logger.info("add_logdb_list_sql=[%s]", add_logdb_list_sql)
            #self._Meta_ChgLogdbDict[chg_logdb_key]
            #cFromDataIP,cToDataIP
            for chg_logdb_key in self._Meta_ChgLogdbDict:
                iDistrictID = str(chg_logdb_key[:chg_logdb_key.find("-")])
                #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                #
                #   bug->20130719->chg_logdb_key还是旧的，那么就是错误的，无法更新，因为旧的有唯一的Key了
                #
                add_logdb_param =(str(iDistrictID)+"-"+str(self._Meta_ChgLogdbDict[chg_logdb_key]["cDataIP"]), str(self._Meta_iSerID), str(self._Meta_ChgLogdbDict[chg_logdb_key]["cDataIP"]),\
                                            str(self._Meta_ChgLogdbDict[chg_logdb_key]["cDBName"]),\
                                            str(self._Meta_ChgLogdbDict[chg_logdb_key]["iPort"]),\
                                            str(self._Meta_ChgLogdbDict[chg_logdb_key]["cDBChar"]),\
                                            str(self._Meta_ChgLogdbDict[chg_logdb_key]["iStatus"]),iDistrictID, \
                                            str(self._Meta_ChgLogdbDict[chg_logdb_key]["cCCWorldID"]),\
                                            str(self._Meta_ChgLogdbDict[chg_logdb_key]["cIDC"]), \
                                            str(self._Meta_ChgLogdbDict[chg_logdb_key]["tlog_path"]))
                self.logger.info("iDistrictID[%s]cDataIP[%s]", iDistrictID, str(self._Meta_ChgLogdbDict[chg_logdb_key]["cDataIP"]))
                res,rows,desc = mysql_new_meta_conn.execute(add_logdb_list_sql, param=add_logdb_param)                        
            #再删除
                del_logdb_list_sql="update db_MetaDataMap.md_data_district set iStatus=-1 where cDistrictID=%s and iSerID=%s"
                self.logger.info("del_logdb_list_sql=[%s]", del_logdb_list_sql)
                #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                del_logdb_param =(chg_logdb_key,  str(self._Meta_iSerID))
                self.logger.info("chg_logdb_key[%s]iSerID[%s]", chg_logdb_key,  str(self._Meta_iSerID))
                
                res,rows,desc = mysql_new_meta_conn.execute(del_logdb_list_sql, param=del_logdb_param)
                
                iDataID = "1"
                iOperType = "33"   #LOGDB的IP变更
                iOperRes = "1"     #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "新变更大区["+iDistrictID+"]的Logdb的IP("+str(self._Meta_ChgLogdbDict[chg_logdb_key]["cFromDataIP"])+")为新的IP("+str(self._Meta_ChgLogdbDict[chg_logdb_key]["cToDataIP"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error insert"
                
                # 如果logpath为空，那么不需要更新事件
                #           add by asherzhou 20130702
                if str(self._Meta_ChgLogdbDict[chg_logdb_key]["tlog_path"]) == "":
                    continue
                

                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn,redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=str(self._Meta_ChgLogdbDict[chg_logdb_key]["cFromDataIP"]), vField2=str(self._Meta_ChgLogdbDict[chg_logdb_key]["cToDataIP"]), vField3=str(self._Meta_ChgLogdbDict[chg_logdb_key]["tlog_path"]))    
                
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaServiceLogdb Error Catch A Exception ="+str(e))

    """ 
        删除META的业务的Logdb的信息 (((调用DBproxy)))
    
    """
    def delMetaServiceLogdb(self,mysql_new_meta_conn,redis_conn):
        try:
            del_logdb_list_sql="update db_MetaDataMap.md_data_district set iStatus=-1 where cDistrictID=%s and iSerID=%s"
            self.logger.info("del_logdb_list_sql=[%s]", del_logdb_list_sql)
            for del_logdb_key in self._Meta_DelLogdbDict:
                #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                iDistrictID = str(del_logdb_key[:del_logdb_key.find("-")])
                del_logdb_param =(del_logdb_key,  str(self._Meta_iSerID))
                self.logger.info("del_logdb_key[%s]iSerID[%s]", del_logdb_key,  str(self._Meta_iSerID))
                
                res,rows,desc = mysql_new_meta_conn.execute(del_logdb_list_sql, param=del_logdb_param)
                self.logger.info("rows=[%d]", rows)
                iDataID = "1"
                vOper = "CC配置系统同步"
                iOperType = "32"   #LOGDB的IP下架
                iActionType = "3"   #（0:默认动作,1:增加动作,2:修改动作,3:删除动作）'
                vFromValue = str(self._Meta_DelLogdbDict[del_logdb_key]["cDataIP"])
                vToValue = ""
                iOperRes = "1"          #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "下架大区["+iDistrictID+"]的Logdb的IP("+str(self._Meta_DelLogdbDict[del_logdb_key]["cDataIP"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error Update"
                    
                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn,redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=str(self._Meta_DelLogdbDict[del_logdb_key]["cDataIP"]))
                
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("delMetaServiceLogdb Error Catch A Exception ="+str(e))


    """ 
        增加META的业务的Gamedr的信息 (((调用DBproxy)))
    
    """
    def addMetaServiceGamedr(self,mysql_new_meta_conn,redis_conn):
        try:
            add_gamedr_list_sql="insert into db_MetaDataMap.md_data_district(cDistrictID,iSerID,iDataID,cDataIP,cDataHost,iStatus,iDistrictID,cCCWorldID,cIDC) "
            add_gamedr_list_sql+=" values(%s,%s,2,%s,%s,%s,%s,%s,%s)"
            self.logger.info("add_gamedr_list_sql=[%s]", add_gamedr_list_sql)
            
            #'51-10.194.5.86': {'cDataIP': u'10.194.5.86', 'cDataHost': 'gamedr', 'cCCWorldID': u'world_51', 'cIDC': u'\u4e0a\u6d77\u7535\u4fe1\u5e02\u5317DC', 'iDistrictID': '51', 'iStatus': '1'}}}
            for add_gamedr_key in self._Meta_AddGamedrDict:
                add_gamedr_param =(add_gamedr_key, str(self._Meta_iSerID), str(self._Meta_AddGamedrDict[add_gamedr_key]["cDataIP"]),\
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["cDataHost"]),\
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["iStatus"]),\
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["iDistrictID"]), \
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["cCCWorldID"]),\
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["cIDC"]))
                
                self.logger.info("iDistrictID[%s]cDataHost[%s]cDataIP[%s]", \
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["iDistrictID"]),\
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["cDataHost"]),\
                                            str(self._Meta_AddGamedrDict[add_gamedr_key]["cDataIP"]))
                
                res,rows,desc = mysql_new_meta_conn.execute(add_gamedr_list_sql, param=add_gamedr_param)
                self.logger.info("rows=[%d]", rows)
                iDataID = '2'
                iDistrictID = str(self._Meta_AddGamedrDict[add_gamedr_key]["iDistrictID"])
                vOper = "CC配置系统同步"
                iOperType = "41"   #GameDr的IP增加
                iActionType = "1"   #（0:默认动作,1:增加动作,2:修改动作,3:删除动作）'
                vFromValue = ""
                vToValue = str(self._Meta_AddGamedrDict[add_gamedr_key]["cDataIP"])
                iOperRes = "1"          #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "新增加大区["+str(self._Meta_AddGamedrDict[add_gamedr_key]["iDistrictID"])+"]的GameDr["+str(self._Meta_AddGamedrDict[add_gamedr_key]["cDataHost"])+"]的IP("+str(self._Meta_AddGamedrDict[add_gamedr_key]["cDataIP"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error Insert"
                
                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn,redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=self._Meta_AddGamedrDict[add_gamedr_key]["cDataIP"])  
                
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaServiceGamedr Error Catch A Exception ="+str(e))


    """ 
        修改META的业务的Gamedr的信息
    """
    def chgMetaServiceGamedr(self,mysql_new_meta_conn,redis_conn):
        try:
            #先增加
            
            add_gamedr_list_sql="insert into db_MetaDataMap.md_data_district(cDistrictID,iSerID,iDataID,cDataIP,cDataHost,iStatus,iDistrictID,cCCWorldID,cIDC) "
            add_gamedr_list_sql+=" values(%s,%s,2,%s,'',%s,%s,%s,%s)"
            self.logger.info("add_gamedr_list_sql=[%s]", add_gamedr_list_sql)
            #self._Meta_ChgGamedrDict[chg_gamedr_key]
            #cFromDataIP,cToDataIP
            for chg_gamedr_key in self._Meta_ChgGamedrDict:
                iDistrictID = str(chg_gamedr_key[:chg_gamedr_key.find("-")])
                #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                add_gamedr_param =(chg_gamedr_key, str(self._Meta_iSerID), str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cDataIP"]),\
                                            str(self._Meta_ChgGamedrDict[chg_gamedr_key]["iStatus"]),iDistrictID, \
                                            str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cCCWorldID"]),\
                                           str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cIDC"]))
                self.logger.info("iDistrictID[%s]cDataIP[%s]", iDistrictID, str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cDataIP"]))
                res,rows,desc = mysql_new_meta_conn.execute(add_gamedr_list_sql, param=add_gamedr_param)                        
            
            #再删除
                del_gamedr_list_sql="update db_MetaDataMap.md_data_district set iStatus=-1 where cDistrictID=%s and iSerID=%s"
                self.logger.info("del_gamedr_list_sql=[%s]", del_gamedr_list_sql)
                #"iStatus":"1","cIDC":"济南联通担山屯AC", "cDataIP":"10.186.0.17", "cCCWorldID":"world_2","iDistrictID":"2"},
                del_gamedr_param =(chg_gamedr_key,  str(self._Meta_iSerID))
                self.logger.info("chg_gamedr_key[%s]iSerID[%s]", chg_gamedr_key,  str(self._Meta_iSerID))
                
                res,rows,desc = mysql_new_meta_conn.execute(del_gamedr_list_sql, param=del_gamedr_param)
                    
                iDataID = "2"
                iOperType = "43"   #GameDR的IP变更
                iOperRes = "1"     #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "新变更大区["+iDistrictID+"]的GameDR的IP("+str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cFromDataIP"])+")为新的IP("+str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cToDataIP"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error insert"
                    
                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn,redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cFromDataIP"]), vField2=str(self._Meta_ChgGamedrDict[chg_gamedr_key]["cToDataIP"]))
                
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaServiceLogdb Error Catch A Exception ="+str(e))



    """ 
        删除META的业务的Gamedr的信息 (((调用DBproxy)))
    
    """
    def delMetaServiceGamedr(self,mysql_new_meta_conn,redis_conn):
        try:
            del_gamedr_list_sql="update db_MetaDataMap.md_data_district set iStatus=-1 where cDistrictID=%s and iSerID=%s"
            self.logger.info("del_gamedr_list_sql=[%s]", del_gamedr_list_sql)
            #'14-10.157.57.35': {'iDistrictID': '14', 'cDataHost': 'gamedr', 'cDistrictID': '14-10.157.57.35', 'cCCWorldID': 'None', 'cDataIP': '10.157.57.35', 'iStatus': '1'}}}
            for del_gamedr_key in self._Meta_DelGamedrDict:
                del_gamedr_param =(del_gamedr_key,  str(self._Meta_iSerID))
                self.logger.info("del_gamedr_key[%s]iSerID[%s]", del_gamedr_key,  str(self._Meta_iSerID))
                
                res,rows,desc = mysql_new_meta_conn.execute(del_gamedr_list_sql, param=del_gamedr_param)
                self.logger.info("rows=[%d]", rows)
                iDataID = "2"
                iDistrictID = str(self._Meta_DelGamedrDict[del_gamedr_key]["iDistrictID"])
                vOper = "CC配置系统同步"
                iOperType = "42"   #Gamedr的IP删除
                iActionType = "3"   #（0:默认动作,1:增加动作,2:修改动作,3:删除动作）'
                vFromValue = str(self._Meta_DelGamedrDict[del_gamedr_key]["cDataIP"])
                vToValue = ""
                iOperRes = "1"          #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "下架大区["+str(self._Meta_DelGamedrDict[del_gamedr_key]["iDistrictID"])+"]的Gamedr["+str(self._Meta_DelGamedrDict[del_gamedr_key]["cDataHost"])+"]的IP("+str(self._Meta_DelGamedrDict[del_gamedr_key]["cDataIP"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error update"

                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn,redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=str(self._Meta_DelGamedrDict[del_gamedr_key]["cDataIP"]))
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("delMetaServiceGamedr Error Catch A Exception ="+str(e))

    """ 
        删除META的业务的Area的列表 (((调用DBproxy)))
    
    """
    def delMetaServiceArea(self,mysql_new_meta_conn,redis_conn):
        try:
            del_area_list_sql="update db_MetaDataMap.md_service_district set iStatus=-1 where iDistrictID=%s and iSerID=%s"
            self.logger.info("del_area_list_sql=[%s]", del_area_list_sql)
            for del_area_id,del_area  in self._Meta_DelAreaDict.items():
                del_param =(str(del_area_id),str(self._Meta_iSerID))
                self.logger.info("id[%s]serid[%s]", del_area_id, self._Meta_iSerID)
                
                res,rows,desc = mysql_new_meta_conn.execute(del_area_list_sql, param=del_param)
                self.logger.info("rows=[%d]", rows)
                
                iDataID = "4"
                iDistrictID = str(del_area_id)
                
                vOper = "CC配置系统同步"
                iOperType = "12"    #大区关服
                iActionType = "3"   #（0:默认动作,1:增加动作,2:修改动作,3:删除动作）'
                vFromValue = str(del_area_id)
                vToValue = ""
                iOperRes = "1"        #0:默认,1:成功,其他值:都是各个值的返回错误码
                vOperRes = "Success"
                vDesc = "关服大区["+str(del_area_id)+"]("+str(del_area["cDistrictName"])+")"
                if not res:
                    iOperRes = "0"
                    vOperRes = "Error update"
                    
                #add by asherzhou #20130604
                self.addMetaNewEventLog(mysql_new_meta_conn,redis_conn, iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, vField1=str(del_area_id), vField2=str(del_area["cDistrictName"]))
                
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("delMetaServiceArea Error Catch A Exception ="+str(e))

    """ 
        更新META的业务md_service_cc_conf的cCCAreaMD5的信息 (((调用DBproxy)))
    
    """
    def updateMetaAreaMD5(self,mysql_new_meta_conn, MD5=""):
        try:
            update_area_md5_sql="update db_MetaDataMap.md_service_cc_conf set cCCAreaMD5=%s where iSerID=%s and iDataID=1"
            self.logger.info("update_area_md5_sql=[%s]", update_area_md5_sql)
        
            update_param =(str(MD5),str(self._Meta_iSerID))
            self.logger.info("MD5[%s]serid[%s]", MD5, self._Meta_iSerID)
            
            res,rows,desc = mysql_new_meta_conn.execute(update_area_md5_sql, param=update_param)
            self.logger.info("rows=[%d]", rows)
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("updateMetaAreaMD5 Error Catch A Exception ="+str(e))


    """ 
        更新META的业务md_service_cc_conf的cCCLogdbMD5的信息 (((调用DBproxy)))
    
    """
    def updateMetaLogdbMD5(self,mysql_new_meta_conn, MD5=""):
        try:
            update_logdb_md5_sql="update db_MetaDataMap.md_service_cc_conf set cCCModuleMD5=%s where iSerID=%s and iDataID=1"
            self.logger.info("update_logdb_md5_sql=[%s]", update_logdb_md5_sql)
        
            update_param =(str(MD5),str(self._Meta_iSerID))
            self.logger.info("MD5[%s]serid[%s]", MD5, self._Meta_iSerID)
            
            res,rows,desc = mysql_new_meta_conn.execute(update_logdb_md5_sql, param=update_param)
            self.logger.info("rows=[%d]", rows)
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("updateMetaLogdbMD5 Error Catch A Exception ="+str(e))



    """ 
        更新META的业务md_service_cc_conf的cCCGamedrMD5的信息 (((调用DBproxy)))
    
    """
    def updateMetaGamedrMD5(self, mysql_new_meta_conn, MD5={}):
        try:
            update_gamedr_md5_sql="update db_MetaDataMap.md_service_cc_conf set cCCModuleMD5=%s where iSerID=%s and iDataID=2"
            self.logger.info("update_gamedr_md5_sql=[%s]", update_gamedr_md5_sql)
            #转移字符
            MD5 = str_escape_string(json.dumps(MD5))
            update_param =(str(MD5),str(self._Meta_iSerID))
            self.logger.info("MD5[%s]serid[%s]", str(MD5), self._Meta_iSerID)
            
            res,rows,desc = mysql_new_meta_conn.execute(update_gamedr_md5_sql, param=update_param)
            self.logger.info("rows=[%d]", rows)
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("updateMetaGamedrMD5 Error Catch A Exception ="+str(e))

    """ 
        增加META的业务事件变更md_oper_event_conf配置 (((调用DBproxy)))
    
    """
    def addMetaOperEventConf(self, mysql_new_meta_conn, iOperType, vOperDesc, vOperContent):
        try:
            add_open_event_sql="insert into db_MetaDataMap.md_oper_event_conf(iOperType,vOperDesc,vOperContent) values(%s,%s,%s)"
            self.logger.info("add_open_event_sql=[%s]", add_open_event_sql)

            area_open_event_param =(str(iOperType),str(vOperDesc), str(vOperContent))
            
            self.logger.info("iOperType[%s]vOperDesc[%s]vOperContent[%s]", iOperType, vOperDesc, vOperContent)
            
            res,rows,desc = mysql_new_meta_conn.execute(add_open_event_sql, param=area_open_event_param)
            self.logger.info("rows=[%d]", rows)

        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaOperEventConf Error Catch A Exception ="+str(e))
    """ 
        增加META的业务事件变更md_oper_event_log_201304变更内容 (((调用DBproxy)))
            
            ---v1.01 
                ---a.加入iDataID  数据类型
                ---b.加入iDistrictID 业务大区ID
                                            ---add by asherzhou 20130514
    """
    def addMetaOperEventLog(self, mysql_new_meta_conn, vOper, iOperType, iDataID, iDistrictID, iActionType, vFromValue, vToValue, iOperRes, vOperRes, vDesc):
        try:
            
            table = "db_MetaDataMap.md_oper_event_log_"+time.strftime("%Y%m",time.localtime())

            add_open_event_sql="insert into "+str(table)+"(iSerID,dtEventTime,vOper,iOperType,iDataID,iDistrictID,iActionType,vFromValue,vToValue,iOperRes,vOperRes,vDesc) "
            add_open_event_sql+=" values(%s,now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            self.logger.info("add_open_event_sql=[%s]", add_open_event_sql)

            area_open_event_param =(self._Meta_iSerID, str(vOper),str(iOperType),str(iDataID),str(iDistrictID),str(iActionType),str(vFromValue), str(vToValue), str(iOperRes), str(vOperRes), str(vDesc))
            
            self.logger.info("vOper[%s]iOperType[%s]iActionType[%s]iDataID[%s]iDistrictID[%s]vFromValue[%s]vToValue[%s]iOperRes[%s]vOperRes[%s]vDesc[%s]", \
                             vOper, iOperType, iActionType,str(iDataID), str(iDistrictID), vFromValue,  vToValue, iOperRes, vOperRes, vDesc)
            
            res,rows,desc = mysql_new_meta_conn.execute(add_open_event_sql, param=area_open_event_param)
            self.logger.info("rows=[%d]", rows)
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaOperEventLog Error Catch A Exception ="+str(e))
            
    """ 
        增加META的业务事件变更md_new_event_log_201306变更内容
            ---v1.2D
                ---add by asherzhou 20130604
    """
    def addMetaNewEventLog(self,mysql_new_meta_conn,redis_conn,iOperType, iDistrictID, iDataID, iOperRes, vOperRes, vDesc, \
                           vField1='0', vField2='0', vField3='0', vField4='0', vField5='0', vField6='0', vField7='0', vField8='0'):
        try:
            
            table = "db_MetaDataMap.md_new_event_log_"+time.strftime("%Y%m",time.localtime())

            add_open_event_sql = "insert into "+str(table)+"(iSerID,dtEventTime,iOperType,iDistrictID,iDataID,iOperRes,vOperRes,vDesc,"
            add_open_event_sql += "vField1, vField2, vField3, vField4, vField5, vField6, vField7, vField8)"
            add_open_event_sql += " values(%s,now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            
            self.logger.info("add_open_event_sql=[%s]", add_open_event_sql)

            area_open_event_param =(self._Meta_iSerID, str(iOperType),str(iDistrictID),str(iDataID),str(iOperRes),str(vOperRes),str(vDesc),\
                                     str(vField1), str(vField2), str(vField3), str(vField4), str(vField5), str(vField6), str(vField7), str(vField8))
            self.logger.info("area_open_event_param=[%s]", repr(area_open_event_param))
            
            res,rows,desc = mysql_new_meta_conn.execute(add_open_event_sql, param=area_open_event_param)
            
            self.logger.info("rows=[%d]", rows)
            
            #发布（pub）ImetaEvent.str(iOperType)
            if redis_conn != None:
                
                message = {}
                message["iSerID"] = str(self._Meta_iSerID)
                message["iOperType"] = str(iOperType)
                message["iDistrictID"] = str(iDistrictID)
                message["iDataID"] = str(iDataID)
                message["iOperRes"] = str(iOperRes)
                message["vOperRes"] = str(vOperRes)
                message["vDesc"] = str(vDesc)
                message["vField1"] = str(vField1)
                message["vField2"] = str(vField2)
                message["vField3"] = str(vField3)
                message["vField4"] = str(vField4)
                message["vField5"] = str(vField5)
                message["vField6"] = str(vField6)
                message["vField7"] = str(vField7)
                message["vField8"] = str(vField8)
                
                redis_conn.publish("ImetaEvent."+str(iOperType),json.dumps(message))
            
        except Exception as e:
            self.logger.error("Catch A Exception[%s]", e)
            raise Exception("addMetaNewEventLog Error Catch A Exception ="+str(e))
            
