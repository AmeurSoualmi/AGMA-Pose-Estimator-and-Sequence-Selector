# AGMA-PESS
Deep learning based video sequence selector for infants GMA
AGMA-PESS is a python (PyQt5) based application developed to facilitate the selection of general movements sequences from videos . 

<img width="1427" height="586" alt="image" src="https://github.com/user-attachments/assets/98d3d92c-fb4b-43a4-b200-851ea8a6528d" />




## How to run AGMA-PESS
Clone this repository and install the required packages listed in requirements.txt. Then, add the deep-learning models (Darpose32_retrained & fasterrcnn) that can be found [here](https://drive.google.com/drive/folders/1fsoi88-NYPsSb9SBCgcLPrs-1JIxiuL5?usp=sharing) inside "models" folder. Finally, run AGMA-PESS.py. 

### Tutorial
A video tutorial of AGMA-PESS is avaliable online [here](https://www.frontiersin.org/journals/pediatrics/articles/10.3389/fped.2024.1465632/full#supplementary-material)

### Instalation file:
Alternatively, you can download directly the installation file (AGMA-PESS_installer.exe) for Windows operating systems, from [here](https://drive.google.com/drive/folders/1fsoi88-NYPsSb9SBCgcLPrs-1JIxiuL5?usp=sharing). 
 

Currently there is no updated version of AGMA-PESS for Mac or Linux.
## Citation
If you use this code, please cite:

- Soualmi A, Alata O, Ducottet C, Petitjean-Robert A, Plat A, Patural H,  Giraud A. AGMA-PESS: a deep learning-based infant pose estimator and sequence selector software for general movement assessment. Frontiers in Pediatrics. 2024; doi: 12. 10.3389/fped.2024.1465632. 

- Soualmi A, Ducottet C, Patural H, Giraud A, Alata O. A 3D pose estimation framework for preterm infants hospitalized in the Neonatal Unit. Multimedia Tools and Applications. 2023; doi: 10.1007/s11042-023-16333-6.




Many thanks for the authors of the following works:
```
@inproceedings{sun2019deep,
  title={Deep High-Resolution Representation Learning for Human Pose Estimation},
  author={Sun, Ke and Xiao, Bin and Liu, Dong and Wang, Jingdong},
  booktitle={CVPR},
  year={2019}
}

@InProceedings{Zhang_2020_CVPR,
    author = {Zhang, Feng and Zhu, Xiatian and Dai, Hanbin and Ye, Mao and Zhu, Ce},
    title = {Distribution-Aware Coordinate Representation for Human Pose Estimation},
    booktitle = {IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    month = {June},
    year = {2020}
}
```
