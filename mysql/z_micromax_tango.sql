USE tango;


INSERT INTO `device`
VALUES ('Micromax/Door/01','Door_Micromax','Micromax','Door','01',0,'nada','nada','Sardana/micromax',0,'Door','0','2023-06-29 09:05:13',NULL,NULL),
       ('dserver/Sardana/micromax',NULL,'dserver','Sardana','micromax',0,'nada','nada','Sardana/micromax',0,'DServer','0',NULL,NULL,NULL),
       ('MacroServer/micromax/1','MS_micromax_1','MacroServer','micromax','1',0,'nada','nada','Sardana/micromax',0,'MacroServer','0','2023-06-29 09:05:13',NULL,NULL),
       ('pool/micromax/1','Pool_micromax_1','pool','micromax','1',0,'nada','nada','Sardana/micromax',0,'Pool','0','2023-06-29 09:05:13',NULL,NULL),
       ('tango/admin/aff41398c13a',NULL,'tango','admin','aff41398c13a',0,'nada','nada','Starter/aff41398c13a',0,'Starter','0',NULL,NULL,NULL),
       ('dserver/Starter/aff41398c13a',NULL,'dserver','Starter','aff41398c13a',0,'nada','nada','Starter/aff41398c13a',0,'DServer','0',NULL,NULL,NULL),
       ('B312a-EH/DIA/DET-01',NULL,'B312a-EH','DIA','DET-01',0,'nada','nada','Eiger/Micromax',0,'Eiger','0',NULL,NULL,NULL),
       ('dserver/Eiger/Micromax',NULL,'dserver','Eiger','Micromax',0,'nada','nada','Eiger/Micromax',0,'DServer','0',NULL,NULL,NULL),
       ('controller/fauxmotorcontroller/faux_ctrl','faux_ctrl','controller','fauxmotorcontroller','faux_ctrl',1,'IOR:010000001700000049444c3a54616e676f2f4465766963655f353a312e3000000100000000000000ac000000010102000c0000003137322e32312e302e313000cbd000000e000000fe66a4cb6400000019000000000600000300000000000000080000000100000000545441010000001c000000010000000100010001000000010001050901010001000000090101000254544140000000010000000d00000062613032386562373033313800000000240000002f746d702f6f6d6e692d726f6f742f3030303030303032352d3136393130363734393400','ba028eb70318','Sardana/micromax',25,'Controller','5','2023-08-03 12:59:33',NULL,NULL),
       ('motor/faux_ctrl/1','mono_energy','motor','faux_ctrl','1',1,'IOR:010000001700000049444c3a54616e676f2f4465766963655f353a312e3000000100000000000000ac000000010102000c0000003137322e32312e302e313000cbd000000e000000fe66a4cb6400000019000000000700000300000000000000080000000100000000545441010000001c000000010000000100010001000000010001050901010001000000090101000254544140000000010000000d00000062613032386562373033313800000000240000002f746d702f6f6d6e692d726f6f742f3030303030303032352d3136393130363734393400','ba028eb70318','Sardana/micromax',25,'Motor','5','2023-08-03 12:59:49',NULL,NULL),
       ('motor/faux_ctrl/2','tabd_zi','motor','faux_ctrl','2',1,'IOR:010000001700000049444c3a54616e676f2f4465766963655f353a312e3000000100000000000000ac000000010102000c0000003137322e32312e302e313100979200000e000000fe5f7bd4640000001b000000000800000300000000000000080000000100000000545441010000001c000000010000000100010001000000010001050901010001000000090101000254544140000000010000000d00000065323330336463636163313800000000240000002f746d702f6f6d6e692d726f6f742f3030303030303032372d3136393136343638313500','e2303dccac18','Sardana/micromax',27,'Motor','5','2023-08-10 05:55:28',NULL,NULL),
       ('B312A-E09/PSS/BS-01',NULL,'B312A-E09','PSS','BS-01',0,'nada','nada','BeamShutter/B312A-PSS',0,'BeamShutter','0',NULL,NULL,NULL),
       ('dserver/BeamShutter/B312A-PSS',NULL,'dserver','BeamShutter','B312A-PSS',0,'nada','nada','BeamShutter/B312A-PSS',0,'DServer','0',NULL,NULL,NULL),
       ('b312-e/ctl/sm-01',NULL,'b312-e','ctl','sm-01',0,'nada','nada','Isara/B312',0,'Isara','0',NULL,NULL,NULL),
       ('dserver/Isara/B312',NULL,'dserver','Isara','B312',0,'nada','nada','Isara/B312',0,'DServer','0',NULL,NULL,NULL),
       ('b312a/vac/plc-01',NULL,'b312a','vac','plc-01',0,'nada','nada','VacPlc01/0',0,'VacPlc01','0',NULL,NULL,NULL),
       ('dserver/VacPlc01/0',NULL,'dserver','VacPlc01','0',0,'nada','nada','VacPlc01/0',0,'DServer','0',NULL,NULL,NULL);



INSERT INTO `property_attribute_device`
VALUES ('motor/faux_ctrl/1','StartPosition','__value',1,'5277.64','2023-08-03 13:01:11','2023-08-03 13:01:11',NULL),
       ('motor/faux_ctrl/2','StartPosition','__value',1,'909.9','2023-08-10 05:55:39','2023-08-10 05:55:39',NULL);


INSERT INTO `property_device`
VALUES ('MacroServer/micromax/1','PoolNames','','','',1,'Pool_micromax_1','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',1,'hoststate','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',2,'1000','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',3,'runningservers','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',4,'1000','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',5,'stoppedservers','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',6,'1000','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',7,'servers','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',8,'1000','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',9,'state','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('tango/admin/aff41398c13a','polled_attr','','','',10,'1000','2023-06-29 09:05:13','2023-06-29 09:05:13',NULL),
       ('pool/micromax/1','PoolPath','','','',1,'/sardana_ctrls','2023-08-03 12:51:06','2023-08-03 12:51:06',NULL),
       ('controller/fauxmotorcontroller/faux_ctrl','type','','','',1,'Motor','2023-08-03 12:59:33','2023-08-03 12:59:33',NULL),
       ('controller/fauxmotorcontroller/faux_ctrl','library','','','',1,'faux.py','2023-08-03 12:59:33','2023-08-03 12:59:33',NULL),
       ('controller/fauxmotorcontroller/faux_ctrl','klass','','','',1,'FauxMotorController','2023-08-03 12:59:33','2023-08-03 12:59:33',NULL),
       ('controller/fauxmotorcontroller/faux_ctrl','id','','','',1,'3','2023-08-03 12:59:33','2023-08-03 12:59:33',NULL),
       ('motor/faux_ctrl/1','id','','','',1,'4','2023-08-03 12:59:49','2023-08-03 12:59:49',NULL),
       ('motor/faux_ctrl/1','ctrl_id','','','',1,'3','2023-08-03 12:59:49','2023-08-03 12:59:49',NULL),
       ('motor/faux_ctrl/1','axis','','','',1,'1','2023-08-03 12:59:49','2023-08-03 12:59:49',NULL),
       ('motor/faux_ctrl/2','id','','','',1,'5','2023-08-10 05:55:28','2023-08-10 05:55:28',NULL),
       ('motor/faux_ctrl/2','ctrl_id','','','',1,'3','2023-08-10 05:55:28','2023-08-10 05:55:28',NULL),
       ('motor/faux_ctrl/2','axis','','','',1,'2','2023-08-10 05:55:28','2023-08-10 05:55:28',NULL),
       ('b312-e/ctl/sm-01','host','','','',1,'b-micromax-isara-0','2023-08-04 15:13:18','2023-08-04 15:13:18',NULL);

