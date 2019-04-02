#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 08/11/18

@author: Anonymous authors
"""

from Data_manager.IncrementalSparseMatrix import IncrementalSparseMatrix

import os, pickle

from Data_manager.split_functions.split_train_validation import split_data_train_validation_test_negative_user_wise

from Data_manager.load_and_save_data import save_data_dict, load_data_dict


class LastFMReader(object):


    def __init__(self):

        super(LastFMReader, self).__init__()


        pre_splitted_path = "Data_manager_split_datasets/LastFM/KDD/MCRec_our_interface/"

        pre_splitted_filename = "splitted_data"

        original_data_path = "Conferences/KDD/MCRec_github/Dataset-In-Papers_master/LastFM/"

        # If directory does not exist, create
        if not os.path.exists(pre_splitted_path):
            os.makedirs(pre_splitted_path)

        try:

            print("LastFMReader: Attempting to load pre-splitted data")

            for attrib_name, attrib_object in load_data_dict(pre_splitted_path, pre_splitted_filename).items():
                self.__setattr__(attrib_name, attrib_object)


        except FileNotFoundError:

            print("LastFMReader: Pre-splitted data not found, building new one")

            print("LastFMReader: loading URM")

            URM_all_builder = self._loadURM(original_data_path + "user_artist.dat", separator="\t")

            URM_all = URM_all_builder.get_SparseMatrix()


            self.URM_train, self.URM_validation, self.URM_test, self.URM_test_negative = split_data_train_validation_test_negative_user_wise(URM_all, negative_items_per_positive = 50)


            user_id_to_index_mappper = URM_all_builder.get_row_token_to_id_mapper()
            item_id_to_index_mappper = URM_all_builder.get_column_token_to_id_mapper()

            ICM_tag = self._loadICM (original_data_path + "artist_tag.dat", item_id_to_index_mappper,
                                     header = False, separator="\t")


            ICM_tag = ICM_tag.get_SparseMatrix()

            self.ICM_dict = {"ICM_tag": ICM_tag}


            data_dict = {
                "URM_train": self.URM_train,
                "URM_test": self.URM_test,
                "URM_validation": self.URM_validation,
                "URM_test_negative": self.URM_test_negative,
                "ICM_dict": self.ICM_dict,
            }

            save_data_dict(data_dict, pre_splitted_path, pre_splitted_filename)

            print("LastFMReader: loading complete")





    def _loadURM (self, filePath, header = False, separator="::"):

        URM_all_builder = IncrementalSparseMatrix(auto_create_col_mapper=True, auto_create_row_mapper=True)

        fileHandle = open(filePath, "r")
        numCells = 0

        if header:
            fileHandle.readline()

        for line in fileHandle:
            numCells += 1
            if (numCells % 1000000 == 0):
                print("Processed {} cells".format(numCells))

            if (len(line)) > 1:
                line = line.split(separator)

                line[-1] = line[-1].replace("\n", "")

                user_id = line[0]
                item_id = line[1]

                URM_all_builder.add_data_lists([user_id], [item_id], [1.0])


        fileHandle.close()

        return  URM_all_builder




    def _loadICM (self, filePath, item_id_to_index_mappper, header = False, separator="::"):

        ICM_builder = IncrementalSparseMatrix(n_rows=len(item_id_to_index_mappper),
                                              auto_create_col_mapper=True,
                                              auto_create_row_mapper=False)

        fileHandle = open(filePath, "r")
        numCells = 0

        if header:
            fileHandle.readline()

        for line in fileHandle:
            numCells += 1
            if (numCells % 1000000 == 0):
                print("Processed {} cells".format(numCells))

            if (len(line)) > 1:
                line = line.split(separator)

                line[-1] = line[-1].replace("\n", "")

                item_id = line[0]
                feature_id = line[1]

                item_index = item_id_to_index_mappper[item_id]

                ICM_builder.add_data_lists([item_index], [feature_id], [1.0])


        fileHandle.close()

        return  ICM_builder