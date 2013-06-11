#!/usr/bin/env python
import sys
from org.apache.log4j import Logger
from org.apache.log4j import Level
from org.apache.log4j import BasicConfigurator
# Log4j configuration
LOG = Logger.getLogger('DataSource Creator')
LOG.setLevel(Level.DEBUG)
BasicConfigurator.configure()
opt = 1

def read(label, default=''):
  print label + ": ",
  input = raw_input().strip()
  return input or default

def main():
  global opt

  server = 'AdminServer'
  user = read('Username [weblogic]','weblogic')
  passwd = read('Password [weblogic]','weblogic')
  host = read('URL do console [localhost:7001]','localhost:7001')

  while opt:
    ds_name = read('Nome do data source [Ex.: BEDS11]', None)
    ds_url = read('Data source URL [Ex.: jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=10.51.160.193)(PORT=1521)))(CONNECT_DATA=(SERVICE_NAME=pcdbaevl)(SERVER=DEDICATED)))]', None)
    jndi_name = read('JNDI Name do data source [Ex.: CC_DS21]', None)
    user_name = read('User name do schema [cliprov2_10]', 'cliprov2_10')
    password = read('Password do schema [clipro]', 'clipro')
    LOG.debug("Validando parametros...")
    if not ds_name:
      print "Nome do data source obrigatorio"
      exit('1')

    if not ds_url:
      print "URL do data source obrigatorio"
      exit('1')

    if not jndi_name:
      print "JNDI Name do data source obrigatorio"
      exit('1')
    connect(user, passwd, "t3://" + host)
    LOG.debug("Listando servidores...")
    servers = get('Servers')
    idx = 0
    print "Escolha o servidor para instalar o DataSource:"
    for s in servers:
      print str(idx) + ' - ' + s.getKeyProperty('Name')
      idx = idx + 1

    while true:
      try:
        idx = read('Servidor [0]','0')
        server = servers[int(idx)].getKeyProperty('Name')
        break
      except (IndexError, ValueError):
        print "Opcao invalida, tente novamente..."

    LOG.debug("Servidor escolhido " + server)
    execute(server,ds_name,ds_url,jndi_name,user_name,password)
    opt = int(read('Deseja incluir outro datasource?[0=Não,1=Sim, default 0]','0'))

def execute(server,ds_name,ds_url,jndi_name,user_name,password):
  server_name = server + '_'
  LOG.debug("Executing data source creation...")
  #Start edition
  edit()
  LOG.debug("Edition mode...creating data source:: " + ds_name)
  startEdit()
  LOG.debug("Starting edition mode...creating data source:: " + ds_name)
  cd('/')
  cmo.createJDBCSystemResource(ds_name)

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name)
  cmo.setName(ds_name)

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCDataSourceParams/' + ds_name)
  set('JNDINames',jarray.array([String(jndi_name)], String))

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCDriverParams/' + ds_name)
  cmo.setUrl(ds_url)
  cmo.setDriverName('oracle.jdbc.OracleDriver')
  #setEncrypted('Password', 'Password_1265391515055', 'Script1265391153133Config', 'Script1265391153133Secret')

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCConnectionPoolParams/' + ds_name)
  cmo.setTestTableName('SQL SELECT 1 FROM DUAL\r\n')

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCDriverParams/' + ds_name + '/Properties/' + ds_name)
  cmo.createProperty('user')

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCDriverParams/' + ds_name + '/Properties/' + ds_name + '/Properties/user')
  cmo.setValue(user_name)

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCDriverParams/' + ds_name + '/Properties/' + ds_name)
  cmo.createProperty('password')

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCDriverParams/' + ds_name + '/Properties/' + ds_name + '/Properties/password')
  cmo.setValue(password)

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCDataSourceParams/' + ds_name)
  cmo.setGlobalTransactionsProtocol('OnePhaseCommit')

  cd('/JDBCSystemResources/' + ds_name)
  set('Targets',jarray.array([ObjectName('com.bea:Name=' + server + ',Type=Server')], ObjectName))

  activate()
  #End edition

  #Start edition
  startEdit()

  cd('/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name + '/JDBCConnectionPoolParams/' + ds_name)
  cmo.setInitSql('SQL ALTER SESSION SET NLS_LANGUAGE=\'AMERICAN\' NLS_TERRITORY=\'AMERICA\' NLS_NUMERIC_CHARACTERS = \'.,\'')
  cmo.setTestTableName('SQL SELECT 1 FROM DUAL\r\n')
  cmo.setTestConnectionsOnReserve(true)

  activate()
  #End edition

main()

