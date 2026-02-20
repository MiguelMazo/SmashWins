import pprint, pickle
pkl_file = open('data.pkl', 'rb');
data = pickle.load(pkl_file);
pprint.pprint(data);
pkl_file.close();