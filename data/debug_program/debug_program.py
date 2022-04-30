import os

file_config = os.path.dirname("\\".join(__file__.split("\\")[:-1]))+"\\config.ini"
file_bkp = "config.bkp"
backup_bkp = "config_bkp.bkp"


with open(file_config, "w") as fl_conf, open(file_bkp, "w") as fl_bkp, open(backup_bkp, "r") as bkp_bkp:
    str_bkp_bkp = bkp_bkp.read()
    fl_conf.write(str_bkp_bkp)
    fl_bkp.write(str_bkp_bkp)