import sublime
import sublime_plugin
import subprocess
import json

# Ad Hoc Readme
#
# 1) Go to tools -> Developer -> New Plugin ...
# 2) Overwrite the generated plugin with the contents of this file
# 3) Save, should save to the User folder under packages
# 4) Configure your postgres connection via your settings, 
#    using the settings seen below starting on line 18
# 5) it slows things way down because it re-fires this query over and over
#    so you have to explicitly enable it with the pg_autocomplete_disabled setting
#    (set it to False to enable the plugin)
#
# To use trigger ctrl + space (auto_complete command)

class PostgresAutocomplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        try:
            settings = sublime.load_settings("Preferences.sublime-settings")

            # Set these settings in your preferences to override the defaults
            port = settings.get("pg_autocomplete_port", "5432")
            host = settings.get("pg_autocomplete_host", "localhost")
            db = settings.get("pg_autocomplete_database", "postgres")
            user = settings.get("pg_autocomplete_user", "postgres")
            pwd = settings.get("pg_autocomplete_password", "secret")
            node = settings.get("pg_autocomplete_node", "node")
            disabled = settings.get("pg_autocomplete_disabled", True)
            if (disabled):
                return []

            opts = """ host: '{}', user: '{}', password: '{}', database: '{}', port: '{}' """.format(host, user, pwd, db, port)

            embedded_node_code=r"""
var knex = require('knex');
let opts = {
  client: "postgresql",
  connection: {""" + opts + """}
};
let conn = knex(opts)


conn.raw(
      `
select
    coalesce(
        pg_catalog.col_description(
            c.oid,
            col.ordinal_position
        ),
        'no comment'
    ) as comment,
    col.table_schema,
    c.relname as table_name,
    a.attname as column_name,
    pg_catalog.format_type(
        a.atttypid,
        a.atttypmod
    ) as type,
    case
        when a.attnotnull then 'not nullable'
        else 'nullable'
    end as nullable
from
    pg_class c,
    pg_attribute a,
    pg_type t,
    information_schema.columns col
where
    c.relkind = 'r'
    and a.attnum > 0
    and a.attrelid = c.oid
    and a.atttypid = t.oid
    and relname in(
        select
            distinct table_name
        from
            information_schema.tables t
        where
            t.table_schema not in ('pg_catalog', 'information_schema')
    )
    and table_name = c.relname
    and column_name = a.attname
order by
    table_name DESC, col.ordinal_position ASC;
`
    )
    .then(result => {
      if (result && result.rows) {
        return result.rows.map(r => ({
          label: r.table_schema + "." + r.table_name + "." + r.column_name,
          value: r.column_name,
          comment: r.type + " - " + r.nullable + " - " + r.comment
        }));
      } else {
        return [];
      }
    })
    .catch(e => {
      return [e.message]
    }).then(results => {
      process.stdout.write(JSON.stringify(results));
      process.exit(0);
    });
"""
        # read settings
            res=json.loads(subprocess.check_output([
                node, "-e", embedded_node_code], universal_newlines=True))
            # conn=psycopg.connect("dbname={0} user={1} password={2} host={3}, port={4}".format(db, user, pwd, host, port))
            # connect
            # query
            # return
            # self.view.insert(edit, 0, "Hello, World!")

            sugs = [[el['label'] + '\t' + el['comment'], el['value']] for el in res]
            return sugs
        except Exception as e:

            return [["pg autocomplete failure: {0}".format(e), ""]]