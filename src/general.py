def bison_log(msg):
    log_file = "bison.log"
    with open(log_file, "a+") as f:
        f.write(msg + "\n")