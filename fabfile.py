""" GWW Fabric file for Plone buildouts

This file can be changed to meet the needs of a specific buildout. The Git
submodule `fabric_lib` has generic functions to provision buildout 
environments.

To active the fabric_lib submodule::

  git submodule init
  git submodule update

Fabric uses SSH to send commands to a Appie user. Make sure you create a 
SSH connection to the Appie user. For more info see 'Prepairing Nuffic Appie 
environments' in the docs (./fabric_lib/README.rst).

Usage:: 

  ./bin/fab <fabric command>:<optional parameter>

"""
from fabric.api import env, settings
from fabric.decorators import task, hosts

try:
    from fabric_lib.tasks import (test_connection, pull_modules, restart_instances,
        deploy_buildout, switch_buildout, get_master_slave, prepare_release)
except ImportError:
    print('To active the fabric_lib submodule run:\n'
          '  git submodule init && git submodule update')
    exit(0)

##############
# Appie config
##############

# CHANGE THE FOLLOWING VARIABLE FOR YOUR BUILDOUT / APPIE ENV:

# Name of the appie environment
appie_env = 'appie-env'  
# Module which can be updated using git pull
env.modules = ('project.egg', )  
# Local url to Plone
env.site_url = 'http://localhost:{0}/plone_id/'  
# Git uri to buildout
env.buildout_uri = 'git@git.gw20e.com:Project/buildout-name.git'  
# SSH uri's for acc and prd
env.acc_host = 'app-{0}-acc@cobain.gw20e.com'.format(appie_env)  
env.prd_hosts = (
    'app-{0}-prd@192.168.5.52'.format(appie_env), 
    'app-{0}-prd@192.168.5.53'.format(appie_env),
)   

#############
# Acceptance
#############
@task
@hosts(env.acc_host)
def acc_test():
    """ Test connection """
    test_connection()

@task
@hosts(env.acc_host)
def acc_update(tag=None):
    """ Pull modules in env.modules and restart instances """
    pull_modules(tag=tag)
    restart_instances()

@task
@hosts(env.acc_host)
def acc_deploy():
    """ Create new buildout in release dir """
    deploy_buildout(tag='master')

@task
@hosts(env.acc_host)
def acc_switch():
    """ Switch supervisor in current buildout dir to latest buildout """
    switch_buildout(tag='master')

#############
# Production
#############
@task
def prd_test():
    """ Test connection, returns master/slave hostnames """
    get_master_slave()

@task
def prd_deploy(server, tag=None):
    """ Create new buildout in release dir. 
    When tag is left empty the current date will be used as tag; ie prd-20140104
    """

    cluster = get_master_slave()

    with settings(host_string=cluster[server]):
        deploy_buildout(tag=tag)

@task
def prd_switch(server, tag=None):
    """ Switch supervisor in current buildout dir to latest buildout. 
    When tag is left empty the current date will be used as tag; ie prd-20140104
    """
    cluster = get_master_slave()

    with settings(host_string=cluster[server]):
        switch_buildout(tag=tag)

@task
@hosts(env.prd_hosts)
def prd_update(tag=None):
    """ Pull modules in env.modules and restart instances """
    pull_modules(tag=tag)
    restart_instances()
