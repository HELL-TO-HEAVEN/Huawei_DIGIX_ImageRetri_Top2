# -*- coding: utf-8 -*-


import time
import numpy as np
import random
import os
from os.path import join,dirname,realpath
from torch.utils.data import Dataset
import cv2 as cv
import torch
from torch.utils.data import DataLoader
import torchvision


class train_dataset(Dataset):
    def __init__(self,root_dir,images_per_classes,classes_per_minibatch,transform):
        
        self.transform = transform  # 变换
        self.classes_per_minibatch=classes_per_minibatch
        self.images_per_classes=images_per_classes
        self.minibatch=classes_per_minibatch*images_per_classes

        filename_filted='label_filltered.txt'
        lst=os.listdir(root_dir)
        self.num_all_classes=np.sum(list(map(lambda x: x[-4:]!='.txt', lst)))

        self.data=[[] for i in range(self.num_all_classes)]
        self.data_name=[[] for i in range(self.num_all_classes)]
        self.label=[]

        file = open(join(root_dir,filename_filted)) 
        while 1:
            line = file.readline()
            if not line:
                break
            line=line.strip('\n')
            data_l=line.split(',')
            data_npy=data_l[0][:-3]+'npy'
            self.label.append(int(data_l[1]))
            self.data_name[int(data_l[1])].append(join(root_dir,data_npy))
        file.close()

        
        for class_id in range(len(self.data_name)):
            start=True
            for img_id in range(len(self.data_name[class_id])):
                img_tmp=np.load(self.data_name[class_id][img_id])[np.newaxis,...]
                if start:
                    self.data[class_id]=img_tmp
                    start=False
                else:
                    self.data[class_id]=np.vstack((self.data[class_id],img_tmp))


        self.steps_all=int(len(self.data)/classes_per_minibatch)
        self.read_order=random.sample(range(0,self.num_all_classes),self.num_all_classes)
        
    def __len__(self):#获取总的mini_batch数目
        return self.steps_all

    def __getitem__(self,step):#获取第step个minibatch
        if step>self.steps_all-1:
            print('step_train out of size')
            return

        # class_ids=self.read_order[step*self.classes_per_minibatch:(step+1)*self.classes_per_minibatch]
        class_ids=random.sample(range(0,self.num_all_classes),self.classes_per_minibatch)
        
        
        start=True
        labels=[]

        for class_id in class_ids:
            num=min(self.images_per_classes,len(self.data[class_id]))
            if num<2:
                print('第{}类图片数目不够'.format(class_id))
                continue
            img_ids=random.sample(range(0,len(self.data[class_id])),num)
            for img_id in img_ids:
                
                img_tmp=self.data[class_id][img_id]
                sample = {"image": img_tmp}
                if self.transform:
                    sample = self.transform(sample)  # 对样本进行变换
                img_tmp = sample['image'].unsqueeze(0)

                labels.append(class_id)
                if start:
                    imgs=img_tmp.detach()
                    start=False
                else:
                    imgs=torch.cat((imgs.detach(),img_tmp),dim=0)

        labels=torch.tensor(labels)
        labels=labels.int()
        imgs=imgs

        # with open('/home/yufei/HUW/models/trip_loss/log/tmp_data.txt',"a") as file:   #”w"代表着每次运行都覆盖内容
        #     file.write('===========================================\n')
        return imgs,labels
        
    

if __name__ == '__main__':
    
    tr=train_dataset("/mnt/home/yufei/HWdata/train_data_resize320",\
                images_per_classes=10,\
                classes_per_minibatch=10,\
                transform=None)
    train_loader = DataLoader(dataset=tr, batch_size=1, shuffle=True ,num_workers=8)
    print(tr.__len__())
    tr.steps_all=10
    n=0
    for i in train_loader:
        tr.steps_all=5
        n=n+1
        print(n)

        
    tr.steps_all=5
    n=0
    for i in train_loader:
        n=n+1
        print(n)
    print(tr.__len__())
    tr.__getitem__(0)