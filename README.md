# Prosodic phrase segmentation

!["our proposed system frameworks"](https://github.com/Xuplussss/prosodic-phrase-segmentation/blob/main/SystemFrameworks.png?raw=true)

## 本工具用於對語音訊號切段，切段步驟:
- 靜音段分割，使用praat工具
- 使用SVM對所有frame分類verbal/non-verbal
- 韻律短語演算法對verbal段細分韻律片段
## 1. 安裝套件
```
    download linux OpenSmile-2.1.0 : https://arcgit.wpi.edu/toto/EMOTIVOClean/tree/master/openSMILE-2.1.0
    tar zxvf openSMILE-2.1.0.tar.gz
    cd openSMILE-2.1.0
    sh buildStandalone.sh
    vim ~/.bashrc
    insert at last: export PATH=$PATH:/media/md01/home/cyhkelvin/software/openSMILE-2.1.0/inst/bin
    source ~/.bashrc
    SMILExtract -h
    
    sudo apt install sox
    sudo apt install lame
    sudo apt install libsox-fmt-all
    chmod 777 praat praat-ft-annot createSILtg.praat svm-predict svm-scale svm-train
```
## 2. 更改 run_segmentaion.sh檔案中的路徑參數
```
    monowav.py:
        file_path原始資料路徑
    main_edit.py:
        當前絕對路徑
        經由monowav.py得到的revised路徑
```
## 3. 執行
```
run_segmentaion.sh
```
