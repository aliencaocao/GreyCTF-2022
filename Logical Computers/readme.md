# Misc - Logical Computers - 456pts

## Description
Teaching computers is like teaching children, you gotta start simple. Today I taught it to recognize the flag!

## Problem Statement

We are given a Python script and a `model.pth` file.

chall.py:
```python
import torch

def tensorize(s : str) -> torch.Tensor:
  return torch.Tensor([(1 if (ch >> i) & 1 == 1 else -1) for ch in list(map(ord, s)) for i in range(8)])

class NeuralNetwork(torch.nn.Module):
  def __init__(self, in_dimension, mid_dimension, out_dimension=1):
    super(NeuralNetwork, self).__init__()
    self.layer1 = torch.nn.Linear(in_dimension, mid_dimension)
    self.layer2 = torch.nn.Linear(mid_dimension, out_dimension)

  def step_activation(self, x : torch.Tensor) -> torch.Tensor:
    x[x <= 0] = -1
    x[x >  0] = 1
    return x

  def forward(self, x : torch.Tensor) -> int:
    x = self.layer1(x)
    x = self.step_activation(x)
    x = self.layer2(x)
    x = self.step_activation(x)
    return int(x)

flag = input("Enter flag: ")
in_data = tensorize(flag)
in_dim	= len(in_data)

model = NeuralNetwork(in_dim, 1280)
model.load_state_dict(torch.load("model.pth"))

if model(in_data) == 1:
	print("Yay correct! That's the flag!")
else:
	print("Awww no...")
```

The challenge is for us to come up with a specific input that can result in an output of 1.

### Notes
This challenge is hard for those that has completely no experience with machine learning, as it would require them to develop inequalities to solve using solvers. However, there is actually a way faster way to do this challenge, if one understands the basics of `PyTorch` (a machine learning library) and its saved models.

As I do have some experience with machine learning, I will explain the faster method in this writeup, without going into details of how each part of the model works. You can visit the [PyTorch documentation](https://pytorch.org/docs/stable/index.html) for more information on that.

## Solving

Let's first analyse what the model does. It takes in a string of unknown length (we can find out the expected length later by inspecting the weights of the first layer), pass it through a linear layer that has 1280 neurons, and then pass it through a custom activation function. The output shape of the first linear layer is (1280,) and the output shape of the second linear layer is (1,). The custom activation function simply changes all negative numbers (including zero) to -1 and all positive numbers to 1.

A `linear` layer is a matrix multiplication between the input and the weights, then added to the biases. E.g. `y = wx + b`, where `y` is the output, `x` is the input, `w` is weights, `b` is biases. This resembles a linear graph `y = mx + c`, thus the name `linear` layer.

There is a custom `Tensorize` function to convert input text to numbers, however that will not be our focus for now since we need to reverse model to find the numerical input first.

The weights of the linear layers are stored in the `model.pth` file. We run the provided code up to the `model.load_state_dict` line to load the weights for inspection. Note that we do not know the input dimension yet, thus you can just type in anything for the flag, and infer the expected input shape from the error message. For example, you can input "A" and observe the error message `RuntimeError: Error(s) in loading state_dict for NeuralNetwork:
	size mismatch for layer1.weight: copying a param with shape torch.Size([1280, 160]) from checkpoint, the shape in current model is torch.Size([1280, 8]).`. This tells us two things:

1. Each character in the input string is being converted to 8 numbers
2. The model expects 160 numbers, which means 20 characters of string.

Knowing this, we can manually change the `in_dim` parameter to `160` to load the model weights successfully.

We can access the weights of a PyTorch layer by accessing the `weight.T` attribute of the `layer` object. E.g. the weight matrix of the first linear layer can be accessed using `model.layer1.weight.T`.

Now comes the important part that allows us to quickly reverse the model: PyTorch models are saved with gradient information. This means that we can use `torch.matmul` to do matrix multiplication between the weights and another matrix in both directions. If we want to do a forward pass (input -> output), we put the input in the first argument of `torch.matmul` and the weights in the second argument. If we want to do a backward pass (output -> input), we put the output in the first argument and the weights in the second argument. Our goal here is a backward pass, or simply reverse of the forward pass.

We can reverse this step by step:
1. Create a `torch.Tensor` that contains only an integer `1`. This is our expected output.
2. We are starting from the last linear layer, working backwards to the first layer. We can simply ignore all the activation functions for this case because they do not result in a sign change. E.g. throughout the model, a positive number will always stay positive. The activation function only affects its magnitude, which is not important for us until the last step.
3. Minus off the bias of the second linear layer from this integer `1`. We do this before the matrix multiplication as multiplication is always done first in the forward pass, so we have to do it the reverse order.
```python
inv = torch.Tensor([1]) - model.layer2.bias.T
```
3. Do the (inverse) matrix multiplication between the weights of the second linear layer and `inv`.
```python
inv = torch.matmul(model.layer2.weight.T, inv)  # notice how the 'weight' is the 'input' argument of torch.matmul
```
4. Minus off the bias of the first linear layer from `inv`.
```python
inv -= model.layer1.bias.T
```
5. Do the (inverse) matrix multiplication between the weights of the first linear layer and `inv`.
```python
inv = torch.matmul(model.layer1.weight.T, inv)
```
6. Now then we apply the activation function to convert all negative numbers (and zeros) to -1 and positive numbers to 1. Notice how the `Tensorize` function also outputs only 1 and -1.
```python
inv[inv <= 0] = -1
inv[inv >  0] = 1
```
7. Finally, we can convert the `inv` Tensor to a list, then use a simple for loop to find the original text by reversing the `Tensorize` function.
```python
inv = inv.tolist()  # converts Tensor to list
k = 0
flag = ''
for i in range(20):  # From previous steps we know the length of flag is 20 characters
    j = 1
    n = 0
    for l in range(8):
        if inv[k] == 1:
            n = n + pow(2, l)  # bit shifting
        k += 1
    flag += chr(int(n))
print(flag)
```
We get our flag: `grey{sM0rT_mAch1nE5}`.

The full solve script:
```python
import torch

def tensorize(s : str) -> torch.Tensor:
  return torch.Tensor([(1 if (ch >> i) & 1 == 1 else -1) for ch in list(map(ord, s)) for i in range(8)])

class NeuralNetwork(torch.nn.Module):
  def __init__(self, in_dimension, mid_dimension, out_dimension=1):
    super(NeuralNetwork, self).__init__()
    self.layer1 = torch.nn.Linear(in_dimension, mid_dimension)
    self.layer2 = torch.nn.Linear(mid_dimension, out_dimension)

  def step_activation(self, x : torch.Tensor) -> torch.Tensor:
    x[x <= 0] = -1
    x[x >  0] = 1
    return x

  def forward(self, x : torch.Tensor) -> int:
    x = self.layer1(x)
    x = self.step_activation(x)
    x = self.layer2(x)
    x = self.step_activation(x)
    return int(x)


model = NeuralNetwork(160, 1280)
model.load_state_dict(torch.load("model.pth"))
inv = torch.Tensor([1]) - model.layer2.bias.T
inv = torch.matmul(model.layer2.weight.T, inv)
inv -= model.layer1.bias.T
inv = torch.matmul(model.layer1.weight.T, inv)
inv[inv <= 0] = -1
inv[inv >  0] = 1
inv = inv.tolist()

k = 0
st=''
for i in range(20):
    j=1
    n=0
    for l in range(8):
        if inv[k] == 1.0:
            n=n+pow(2, l)
        k+=1
    st+=chr(int(n))
print(st)
```