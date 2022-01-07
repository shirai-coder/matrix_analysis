import pandas as pd

#異なるfunction間の背反関係の導出(性能を1つのノードとしてみる)
#同function内の背反関係のマトリクスはcalcuation_same_func.ipynbで計算
#計算結果を統合して、tradeoff_dfとする(functionごとの重要度を既に掛けたもの)
#入力は全要素を行列とした影響関係のマトリクス(sample_df)と背反関係のマトリクス(tradeoff_df)
#tradeoff_dfの要素名は、sample_dfと同じにする
#coordintae_dfを下地として、計算結果を入力する

def tradeoffDiff(sample_df, tradeoff_df):
    copy_df = tradeoff_df.copy()

    dp_columns_all = list(sample_df.columns)
    dp_index_all = list(sample_df.index)
    dp_columns = list(tradeoff_df.columns)
    dp_index = list(tradeoff_df.index)

    #dp_index_all-2とdp_indexの長さが等しいことを確認
    if len(dp_columns) == len(dp_index):
        all_element = len(dp_columns)
    else:
        print("背反関係のマトリクスが正しくありません")

    #感度と重要度の積のマトリクスsample_new_df
    ##機能層と説明層を追加 #機能層をint型に変換
    sample_new_df = pd.DataFrame(index=dp_index_all,columns=dp_index_all)
    sample_new_df["説明層"] = sample_df["説明層"]
    sample_new_df["機能層"] = sample_df["機能層"].astype('int')
    sample_new_df.loc["説明層"] = sample_df.loc["説明層"]
    sample_new_df.loc["機能層"] = sample_df.loc["機能層"].astype('int')
    prompt_df = (sample_df.iloc[2:,3:].T*list(sample_df.iloc[2:,2])).T
    prompt_df_max_value = prompt_df.max().max()
    prompt_df = prompt_df/prompt_df_max_value
    for df_index in dp_index:
        for df_col in dp_columns:
            sample_new_df.loc[df_index, df_col] = prompt_df.loc[df_index, df_col]

    #背反関係の強さを導出、関係がない場合は何も記述しない
    tradeoff_list = [] #正規化するため
    name_list = [] #行列の積を導出するため
    importance_df = sample_df.iloc[:,2]



    for df_index in dp_index:
        for df_col in dp_columns:
            #対角行列の属性に0を挿入
            if df_col == df_index :
                tradeoff_df.loc[df_index, df_col] = 0
            #対角以外
            else :
                #column方向に見て説明層が0の時①
                element_func_x = sample_df.loc[df_index, "機能層"]
                element_func_y = sample_df.loc["機能層", df_col]
                df_index_label = sample_df.loc[df_index, "説明層"]
                df_col_label = sample_df.loc["説明層", df_col]
                k = 0
                if sample_df.loc["説明層", df_col] == 0 and sample_df.loc[df_index, "説明層"] != 0 and sample_df.loc[df_index, "機能層"] > sample_df.loc["機能層", df_col] and (df_index_label in sample_df[sample_df["機能層"] == element_func_y]["説明層"].values) == True:
                    #機能層の差分回す
                    for i in range(element_func_x - element_func_y):
                        #機能層が i + element_func_y の時に、df_index_labelがあるか確認
                        if (df_index_label in sample_df[sample_df["機能層"] == i + element_func_y]["説明層"].values) == True :
                            element_df = sample_new_df.loc[(sample_new_df["機能層"] == i + element_func_y) & (sample_new_df["説明層"] == df_index_label), (sample_new_df.loc["機能層"] == i + element_func_y + 1) & (sample_new_df.loc["説明層"] == df_index_label)]
                            if k == 0:
                                name_list = list(element_df.index)
                                middle_df = element_df
                            else:
                                middle_df = middle_df.dot(element_df)
                            k = k + 1
                    for i in name_list:
                        tradeoff_df.loc[df_index,df_col] =  tradeoff_df.loc[df_index,df_col] + middle_df.loc[i,df_index]*copy_df.loc[df_col,i]
                #index方向に見て説明層が0の時②
                elif sample_df.loc["説明層", df_col] != 0 and sample_df.loc[df_index, "説明層"] == 0 and sample_df.loc[df_index, "機能層"] < sample_df.loc["機能層", df_col] and (df_col_label in sample_df[sample_df["機能層"] == element_func_x]["説明層"].values) == True:
                    #機能層の差分回す
                    for i in range(element_func_y - element_func_x):
                        #機能層が i + element_func_x の時に、df_col_labelがあるか確認
                        if (df_col_label in sample_df[sample_df["機能層"] == i + element_func_x]["説明層"].values) == True :
                            element_df = sample_new_df.loc[(sample_new_df["機能層"] == i + element_func_x) & (sample_new_df["説明層"] == df_col_label), (sample_new_df.loc["機能層"] == i + element_func_x + 1) & (sample_new_df.loc["説明層"] == df_col_label)]
                            if k == 0:
                                name_list = list(element_df.index)
                                middle_df = element_df
                            else:
                                middle_df = middle_df.dot(element_df)
                            k = k+ 1
                    for i in name_list:
                        tradeoff_df.loc[df_index,df_col] = tradeoff_df.loc[df_index,df_col] + middle_df.loc[i,df_col]*copy_df.loc[df_index,i]
                #index,column方向どちらも説明層が0ではない時③           
                elif  sample_df.loc["説明層", df_col] != 0 and sample_df.loc[df_index, "説明層"] != 0 and sample_df.loc["機能層", df_col] >= 1 and sample_df.loc[df_index, "機能層"] >= 1:
                    element_func_x = sample_df.loc[df_index, "機能層"]
                    element_func_y = sample_df.loc["機能層", df_col]
                    min_element_func = min(element_func_x, element_func_y)
                    max_element_func = max(element_func_x, element_func_y)
                    element_label_x = sample_df.loc[df_index, "説明層"]
                    element_label_y = sample_df.loc["説明層", df_col]
                    min_element_x = min(sample_df[sample_df["説明層"] == element_label_x]["機能層"])
                    min_element_y = min(sample_df[sample_df["説明層"] == element_label_y]["機能層"])
                    max_element = max(min_element_x, min_element_y)
                    min_element = min(min_element_x, min_element_y)
                    df_index_label = sample_df.loc[df_index, "説明層"]
                    df_col_label = sample_df.loc["説明層", df_col]
                    if max_element <= element_func_x and max_element <= element_func_y :
                        #両方とも過去に同説明層の要素を持っている場合、まず四角形に探索する、min_element_func - max_element=0なら探索しない
                        for i in range(min_element_func - max_element):
                            element_x_df = sample_new_df.loc[(sample_new_df["機能層"] == i + max_element) & (sample_new_df["説明層"] == df_index_label), (sample_new_df.loc["機能層"] == i + max_element + 1) & (sample_new_df.loc["説明層"] == df_index_label)]
                            element_y_df = sample_new_df.loc[(sample_new_df["機能層"] == i + max_element) & (sample_new_df["説明層"] == df_col_label), (sample_new_df.loc["機能層"] == i + max_element + 1) & (sample_new_df.loc["説明層"] == df_col_label)]
                            name_x_in_list = list(element_x_df.index)
                            name_y_in_list = list(element_y_df.index)
                            name_x_col_list = list(element_x_df.columns)
                            name_y_col_list = list(element_y_df.columns)
                            if i == 0:
                                middle_df = copy_df.loc[name_x_col_list, name_y_col_list] + 2*element_x_df.T.dot(copy_df.loc[name_x_in_list, name_y_in_list].dot(element_y_df))
                            else :
                                middle_df = copy_df.loc[name_x_col_list, name_y_col_list] + 2*element_x_df.T.dot(middle_df.dot(element_y_df)) 
                        if min_element_func - max_element == 0:
                            middle_df = copy_df.loc[(sample_new_df["機能層"] == max_element) & (sample_new_df["説明層"] == df_index_label), (sample_new_df.loc["機能層"] == max_element) & (sample_new_df.loc["説明層"] == df_col_label)]
                            name_x_col_list = list(middle_df.index)
                            name_y_col_list = list(middle_df.columns)

                        #両方とも過去に同説明層の要素を持っている場合、上と同じように次に三角形に探索する
                        if element_func_x == element_func_y :
                            tradeoff_df.loc[df_index,df_col] = middle_df.loc[df_index,df_col]
                        else :
                            if element_func_x > element_func_y:
                                middle_df = middle_df.loc[name_x_col_list, df_col]
                                for i in range(element_func_x - element_func_y):
                                    element_df = sample_new_df.loc[(sample_new_df["機能層"] == i + element_func_y) & (sample_new_df["説明層"] == df_index_label), (sample_new_df.loc["機能層"] == i + element_func_y + 1) & (sample_new_df.loc["説明層"] == df_index_label)]
                                    middle_df = middle_df.T.dot(element_df)
                                tradeoff_df.loc[df_index,df_col] = middle_df.loc[df_index]
                            else :
                                middle_df = middle_df.loc[df_index, name_y_col_list]
                                for i in range(element_func_y - element_func_x):
                                    element_df = sample_new_df.loc[(sample_new_df["機能層"] == i + element_func_x) & (sample_new_df["説明層"] == df_col_label), (sample_new_df.loc["機能層"] == i + element_func_x + 1) & (sample_new_df.loc["説明層"] == df_col_label)]
                                    middle_df = middle_df.dot(element_df)
                                tradeoff_df.loc[df_index,df_col] = middle_df.loc[df_col]
                            

                    else :
                        tradeoff_df.loc[df_index,df_col] = 0

                else:
                    tradeoff_df.loc[df_index,df_col] = copy_df.loc[df_index,df_col]

    #正規化するためのリストに数値を加える、無駄に回してしまっている                       
    for df_col in dp_index: 
        for df_index in dp_index:
            tradeoff_list.append(tradeoff_df.loc[df_index,df_col])      

    #背反関係の強さを最大和に合わせて正規化
    tradeoff_sum_max = max(tradeoff_list)
    for df_col in dp_index: 
        for df_index in dp_index:
            if tradeoff_df.loc[df_index,df_col] != "-" and tradeoff_df.loc[df_index,df_col] != "":
                tradeoff_df.loc[df_index,df_col] = float(tradeoff_df.loc[df_index,df_col])/tradeoff_sum_max

    return tradeoff_df