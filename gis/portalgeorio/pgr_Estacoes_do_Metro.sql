SET CLIENT_ENCODING TO UTF8;
SET STANDARD_CONFORMING_STRINGS TO ON;
SELECT DropGeometryColumn('','pgr_estacoes_do_metro','geom');
DROP TABLE "pgr_estacoes_do_metro";
BEGIN;
CREATE TABLE "pgr_estacoes_do_metro" (gid serial,
"fonte" varchar(100),
"linha" varchar(33),
"codestmetr" int4,
"nome" varchar(24));
ALTER TABLE "pgr_estacoes_do_metro" ADD PRIMARY KEY (gid);
SELECT AddGeometryColumn('','pgr_estacoes_do_metro','geom','4326','POINT',2);
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','36','Ipanema / General Osório',ST_Transform('01010000200972000079C7BEE353E62441CB08A5324D725C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','34','Cantagalo',ST_Transform('0101000020097200002CE6D8D811E92441DB8B92F12B735C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','32','Siqueira Campos',ST_Transform('0101000020097200001AEFFECFEEEE2441DAD12BD830745C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','31','Cardeal Arcoverde',ST_Transform('010100002009720000D197F7E38CF324417555F47F7D745C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','30','Botafogo',ST_Transform('01010000200972000084EA2FED56F124414413F5F9E9755C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','29','Flamengo',ST_Transform('010100002009720000F672F88F68F52441446EA74160775C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','28','Largo do Machado',ST_Transform('010100002009720000D6D3082864F62441D915218913785C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','27','Catete',ST_Transform('01010000200972000059FFC97C26F724414BCA79C0A3785C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','17','Saens Peña',ST_Transform('010100002009720000C963824DCBCA244176E9280EEB785C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','18','São Francisco Xavier',ST_Transform('0101000020097200006415837D92D12441A48D290E48795C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','26','Gloria',ST_Transform('01010000200972000001FBB4557FF724411AE6C62E49795C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','19','Afonso Pena',ST_Transform('010100002009720000A2783BE346D624418B74940B8C795C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1- Estacao de Transferencia','16','Estácio',ST_Transform('01010000200972000009FBA7C882DF24414520E042087A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','25','Cinelandia',ST_Transform('0101000020097200006019AB4391F82441C28890822F7A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','14','Maracana',ST_Transform('010100002009720000835DE25D97C924412300DF1C657A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','33','Praca Onze',ST_Transform('01010000200972000071AF7D48A9E42441148487A26A7A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','15','Sao Cristovao',ST_Transform('010100002009720000F23B1EEF13D324415D4BE277717A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','35','Cidade Nova',ST_Transform('0101000020097200006F2B1D05D9DF24416C1CBC4C887A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','24','Carioca',ST_Transform('0101000020097200000434B9E9D7F6244139013C2BA67A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','21','Central',ST_Transform('01010000200972000040C5525BA1EB24413DFB3350F37A5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','22','Presidente Vargas',ST_Transform('010100002009720000CEEE698C37F02441F6E817BC157B5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 1','23','Uruguaiana',ST_Transform('010100002009720000F534F715BFF32441DB991C8F167B5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','13','Triagem',ST_Transform('010100002009720000893D7D016EC124417CE34E96DA7B5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','12','Maria da Graça',ST_Transform('01010000200972000050B31ACFCDB42441996F65108A7D5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','11','Del Castilho',ST_Transform('010100002009720000F162003E88AB24410BCDBB4ED17D5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','10','Inhauma',ST_Transform('0101000020097200008DCE79062DA324413A179DB54B7E5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','9','Engenho da Rainha',ST_Transform('01010000200972000033558938DE9824415C4C6D82F17E5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','8','Tomas Coelho',ST_Transform('01010000200972000050D35CA5E38F24417AD25D14B97F5C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','7','Vicente de Carvalho',ST_Transform('0101000020097200005EF49726D189244112607268AA805C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','6','Iraja',ST_Transform('010100002009720000334D4FD6B3812441D2EDA6D554815C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','5','Colegio',ST_Transform('010100002009720000C6CD3C338B7924418C48487DD6815C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','4','Coelho Neto',ST_Transform('01010000200972000072D9B4FD14732441EED67A6204835C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','3','Acari / Fazenda Botafogo',ST_Transform('01010000200972000027E0016F5B6C2441933B816722845C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','2','Engenheiro Rubens Paiva',ST_Transform('01010000200972000043534372CB6624412DAB64EFAE845C41'::geometry, 4326));
INSERT INTO "pgr_estacoes_do_metro" ("fonte","linha","codestmetr","nome",geom) VALUES ('http://www.metrorio.com.br/Estacoes/','Linha 2','1','Pavuna',ST_Transform('0101000020097200003EE78D5BB5612441304B9427C2855C41'::geometry, 4326));
CREATE INDEX "pgr_estacoes_do_metro_geom_gist" ON "pgr_estacoes_do_metro" USING GIST ("geom");
COMMIT;
