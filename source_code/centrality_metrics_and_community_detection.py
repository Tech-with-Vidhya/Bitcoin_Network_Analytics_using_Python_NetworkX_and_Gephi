### unix to utc -> df['#timestamp'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import networkx as nx
from collections import Counter


def sort_dict(dict_, reverse=True, values=False, top=None):
    """
    Sort a deictionary 
    params
     - dict_ : dictionary to be sorted
     - reverse: True if descending
     - values: returns just the values (not the keys)
     - top: return first top elements , if None return all
    """
    sorted_ = sorted(dict_.items(), key=lambda x: x[1], reverse=reverse)
    if top:
        sorted_ =  sorted_[:top]
    if values:
        return [x[1] for x in sorted_]
    return dict(sorted_)
    

def counter(list_, top = None):
    """
    Get the distribution of entries in list
    """
    count_list = Counter(list_)
    if top:
        dict(count_list.most_common(top))
    return count_list


def plot_hist(list_, fig_size=(20,10), ax=None, x_scale='linear', y_scale='linear', color='darkred'):
    if not ax:
        fig, ax = plt.subplots(figsize=fig_size)
    plt_ = sns.histplot(list_, stat='probability', color='darkred', ax=ax)
    plt_.axes.set_xscale(x_scale)
    plt_.axes.set_yscale(y_scale)

def str_to_date(date, format_='%Y-%m-%d %H:%M:%S'):
    """
    sting to utc timestamp
    """
    return datetime.strptime(date, format_)

def get_ratings(graph, node, to_datetime=False):
    """
    For a given user(node) get all the attributes of incoming liks and out going links
    
    return: in_rating_list: list of attributes of all incoming links to node
            out_rating_list: list of attributes of all outgoing links to node
    """
    in_rating_list = []
    out_rating_list = []
    for neighbor in set(nx.all_neighbors(graph, node)):
        attr_in = graph.get_edge_data(neighbor, node)
        attr_out = graph.get_edge_data(node, neighbor)
        if attr_in:
            attr_in = attr_in.copy()
            if to_datetime: attr_in['time'] = str_to_date(attr_in['time'])
            in_rating_list.append((neighbor,attr_in))
        if attr_out:
            attr_out = attr_out.copy()
            if to_datetime: attr_out['time'] = str_to_date(attr_out['time'])
            out_rating_list.append((neighbor,attr_out))
    return in_rating_list, out_rating_list

def time_interval(edges):
    time_stamps = set([str_to_date(x['time']).date() for x in edges])
    return min(time_stamps), max(time_stamps)

def get_neg_rating_ratio(G, node):
    attrs = G.in_edges(node, data=True)
    neg_ratings = [attr[2]['rating']<0 for attr in attrs]
    if len(neg_ratings) == 0:
        return 0
    return sum(neg_ratings)/len(neg_ratings)

def ones_percent(G, node):
    attrs = G.in_edges(node, data=True)
    ones_ratings = [attr[2]['rating']==1 for attr in attrs]
    if len(ones_ratings) == 0:
        return 0
    return sum(ones_ratings)/len(ones_ratings)

def plot_degree_dist(G, ax):
    in_degree = dict(G.in_degree())
    in_deg_scores = sort_dict(in_degree, values=True)
    plot_hist(in_deg_scores, x_scale='log', ax=ax)
    
def plot_community_distrubution(community_nodes, node_set, ax=None):
    community_ind = []
    community_share = []
    for i, nodes in enumerate(community_nodes):
        appeared_in = set(node_set).intersection(nodes)
        if len(appeared_in)>0:
            community_ind.append(i+1)
            community_share.append(len(appeared_in))
    dict_ = dict(sorted(dict(zip(community_ind, community_share)).items(), key=lambda x: x[1], reverse=True))
    pd_df = pd.DataFrame(list(dict_.items()))
    pd_df.columns =["Community","Count"]
    #print(pd_df)
    sns.barplot(x='Community',y='Count',data=pd_df,order = pd_df['Community'], ax=ax)

def read_community(file, G):
    df = pd.read_csv('community.csv')
    for i, node_list in enumerate(df.groupby(['modularity_class'])['Id'].apply(list)):
        G_sub = G.subgraph(node_list)
        attrs = pd.Series()
        attrs['community_index'] = i
        attrs['num_nodes'] = G_sub.number_of_nodes()
        attrs['num_edges'] = nx.to_undirected(G_sub).number_of_edges()
        attrs['cluster_coeff'] = nx.average_clustering(G_sub)
        attrs['num_traingles'] = sum(nx.triangles(nx.to_undirected(G_sub)).values())/3
        yield attrs

def time_elapsed(t1, t2, to_str=True):
    if to_str:
        t1, t2 = str_to_date(t1), str_to_date(t2)
    delta = t1-t2 if t1>t2 else t2-t1
    return delta.days