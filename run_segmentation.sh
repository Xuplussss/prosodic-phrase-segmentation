#!/bin/bash
# download linux OpenSmile-2.1.0 : https://arcgit.wpi.edu/toto/EMOTIVOClean/tree/master/openSMILE-2.1.0
# tar zxvf openSMILE-2.1.0.tar.gz
# cd openSMILE-2.1.0
# sh buildStandalone.sh
# vim ~/.bashrc
# insert at last: export PATH=$PATH:/media/md01/home/cyhkelvin/software/openSMILE-2.1.0/inst/bin
# source ~/.bashrc
# SMILExtract -h
# 安裝sox
# sudo apt install sox
# sudo apt install lame
# sudo apt install libsox-fmt-all

# python monowav.py /datatank/p76061302_data/file_path/ # 會在相同路徑下生成mono/資料夾存放新的檔案
python main_edit.py /datatank/p76061302_data/segmentation_submit/ /datatank/p76061302_data/ATemotion/Dataset/CMU_MOSEI/Test/
#                      第一個參數放 當前絕對路徑                      第二個參數放 資料存放的絕對路徑
# .textgrid

: <<'END'

END
