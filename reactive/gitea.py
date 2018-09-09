from charms.reactive import (
    when,
    when_not,
    set_flag,
    when_file_changed,
    endpoint_from_flag,
)
from charmhelpers.core import host, hookenv
from charmhelpers.core.templating import render


@when_not('db.connected')
def blocked():
    hookenv.status_set('blocked', 'gitea relation to PostgreSQL is required')


@when('db.connected')
def request_db(pgsql):
    hookenv.status_set('waiting', 'Pending setup of database')
    pgsql.set_database('gitea')


@when('db.master.changed', 'snap.installed.gitea')
def render_config():
    pgsql = endpoint_from_flag('db.master.changed')
    render('app.ini.j2', '/var/snap/gitea/common/conf/app.ini', {
        'db': pgsql.master,
    })
    hookenv.status_set('active', '')
    hookenv.open_port(3000)
    set_flag('gitea.configured')


@when_file_changed('/var/snap/gitea/common/conf/app.ini')
def restart_service():
    host.service_restart('snap.gitea.web')