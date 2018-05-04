from timeit import default_timer
from torch.autograd import Variable
import numpy as np
import torch
from BASIC_LIST.basic import groupby


def groupby(seq, minibatch=10, key='mini'):
	_len = len(seq)
	if(key=='mini'):
		_num = math.ceil(_len*1./minibatch)
	elif(key=='num'):
		_num = minibatch
		minibatch = math.ceil(_len*1./_num)
	_list = []
	for i in range(_num):
		_start = i*minibatch
		if((i+1)*minibatch<_len):
			_end = (i+1)*minibatch
		else:
			_end = _len
		_list.append(seq[_start:_end])
	return _list


class loader:
	def __init__(self, X_path, Y_path, minibatch=1000):
		end = default_timer()
		self.X = np.load(X_path).astype('float32')
		self.Y = (no.load(Y_path)/255).astype('int32')
		self.X, self.Y = self.X.transpose([2, 0, 1]), self.Y.transpose([2, 0, 1])
		self.X = np.expand_dims(self.X, 1)
		print("loading time: ", default_timer()-end)
		self.minibatch = minibatch

	def get(self):
		indices = np.random.permutation(len(self.X)).tolist()
		groups = groupby(indices, self.minibatch, key='mini')
		for index, group in enumerate(groups):
			yield self.X[group], self.Y[group]




def train(model, loader, after_fun=None, correct_fun=None, num_epoch=1000, device=3, savePath="./save/"):
	optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
	loss = torch.nn.CrossEntropyLoss()

	if device is not None:
		loss.cuda(device)
		model.cuda(device)

	end = default_timer()
	for epoch in range(num_epoch):
		correct = 0
		_len = 0
		l = 0
		count = 0
		for index, (X, Y) in enumerate(loader.get()):
			X, Y = Variable(torch.from_numpy(X)), Variable(torch.from_numpy(Y).long())
			if device is not None:
				X = X.cuda(device)
				Y = Y.cuda(device)

			if after_fun is None:
				R = model(X)
			else:
				R = after_fun(*model(X))
			L = loss(R, Y)
			optimizer.zero_grad()
			L.backward()
			optimizer.step()


			pred = R.data.max(1)[1]
			correct += pred.eq(Y.data).sum()
			_len = _len+Y.data.shape[0]
			l = l+L.data.item()
			count = count+1


		###
		# save
		###
		if(epoch%5==0):
			state = model.state_dict()
			torch.save(state, savePath+str(epoch).zfill(6)+".pth.tar")


		if correct_fun is None:
			correct = 100. * correct / _len
		else:
			correct = correct_fun(correct, _len)
		_loss = l/count
		string = "epoch: {}, accuracy: {}, loss: {}, time: {}".format(epoch, correct, _loss, default_timer()-end)
		print(string)
		end = default_timer()