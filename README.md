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