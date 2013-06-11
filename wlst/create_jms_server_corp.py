#!/usr/bin/env python
import sys
from org.apache.log4j import Logger
from org.apache.log4j import Level
from org.apache.log4j import BasicConfigurator
# Log4j configuration
LOG = Logger.getLogger('JMS Creator')
LOG.setLevel(Level.DEBUG)
BasicConfigurator.configure()

def read(label, default=''):
  print label + ": ",
  input = raw_input().strip()
  return input or default

def main():
  server = 'AdminServer'
  user = read('Username [weblogic]','weblogic')
  passwd = read('Password [weblogic]','weblogic')
  host = read('URL do console [localhost:7001]','localhost:7001')
  connect(user, passwd, "t3://" + host)
  servers = get('Servers')
  idx = 0
  print "Escolha o servidor para instalar o JMSServer:"
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

  print "Servidor escolhido " + server
  execute(server)

def execute(server):
  server_name = server + '_'
  LOG.debug("Executing creation...")
  #Start edition
  edit()
  startEdit()
  cmo.createJMSServer(server_name + 'CorporativePortalJMSServer')
  LOG.debug("JMS Server created...")
  cd('/JMSServers/' + server_name + 'CorporativePortalJMSServer')
  LOG.debug("JMS Server setting targets...")
  set('Targets',jarray.array([ObjectName('com.bea:Name=' + server + ',Type=Server')], ObjectName))
  activate()
  #End edition

  #Start edition
  edit()
  startEdit()
  cd('/')
  cmo.createJMSSystemResource(server_name + 'CorporativePortalSystemModule')
  LOG.debug("JMS Module created...")
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule')
  set('Targets',jarray.array([ObjectName('com.bea:Name=' + server + ',Type=Server')], ObjectName))
  activate()
  #End edition

  #Start edition
  edit()
  startEdit()
  cmo.createSubDeployment(server_name + 'CorporativePortalSubdeployment')
  LOG.debug("JMS SubDeployment created...")
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/SubDeployments/' + server_name + 'CorporativePortalSubdeployment')
  set('Targets',jarray.array([ObjectName('com.bea:Name=' + server_name + 'CorporativePortalJMSServer,Type=JMSServer')], ObjectName))
  activate()
  #End edition

  #Start edition
  edit()
  startEdit()
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/JMSResource/' + server_name + 'CorporativePortalSystemModule')
  cmo.createConnectionFactory(server_name + 'CorporativePortalConnectionFactory')
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/JMSResource/' + server_name + 'CorporativePortalSystemModule/ConnectionFactories/' + server_name + 'CorporativePortalConnectionFactory')
  cmo.setJNDIName('CorporativePortalConnectionFactory')
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/JMSResource/' + server_name + 'CorporativePortalSystemModule/ConnectionFactories/' + server_name + 'CorporativePortalConnectionFactory/SecurityParams/' + server_name + 'CorporativePortalConnectionFactory')
  cmo.setAttachJMSXUserId(false)
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/JMSResource/' + server_name + 'CorporativePortalSystemModule/ConnectionFactories/' + server_name + 'CorporativePortalConnectionFactory')
  cmo.setDefaultTargetingEnabled(true)
  activate()
  #End edition

  #Start edition
  edit()
  startEdit()
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/JMSResource/' + server_name + 'CorporativePortalSystemModule')
  cmo.createQueue(server_name + 'CorporativePortalQueue')
  LOG.debug("JMS Queue created...")
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/JMSResource/' + server_name + 'CorporativePortalSystemModule/Queues/' + server_name + 'CorporativePortalQueue')
  cmo.setJNDIName('CorporativePortalQueue')
  cmo.setSubDeploymentName(server_name + 'CorporativePortalSubdeployment')
  LOG.debug("JMS Queue setting targets...")
  cd('/JMSSystemResources/' + server_name + 'CorporativePortalSystemModule/SubDeployments/' + server_name + 'CorporativePortalSubdeployment')
  target = 'com.bea:Name=' + server_name + 'CorporativePortalJMSServer,Type=JMSServer'
  LOG.debug('JMS Queue target ' + target)
  set('Targets',jarray.array([ObjectName('com.bea:Name=' + server_name + 'CorporativePortalJMSServer,Type=JMSServer')], ObjectName))
  activate()
  #End edition

main()
