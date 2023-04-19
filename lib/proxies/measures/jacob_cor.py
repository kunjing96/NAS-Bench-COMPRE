import torch, numpy as np

from lib.proxies.measures import measure


def get_batch_jacobian(net, x):
    net.zero_grad()
    x.requires_grad_(True)
    y = net(x)
    if isinstance(y, tuple):
        y = y[0]
    y.backward(torch.ones_like(y))
    jacob = x.grad

    return jacob.detach()


def eval_score(jacobs, labels):
    corrs = np.corrcoef(jacobs)
    v, _  = np.linalg.eig(corrs)
    k = 1e-5
    score = -np.sum(np.log(v + k) + 1./(v + k))
    return score


@measure('jacob_cor', bn=True, mode='param')
def compute_jacob_cor(net, device, inputs, targets, mode, loss_fn, split_data=1):
    jacobs  = []
    N = inputs.shape[0]
    for sp in range(split_data):
        net.zero_grad()

        st=sp*N//split_data
        en=(sp+1)*N//split_data

        jacobs_batch = get_batch_jacobian(net, inputs[st:en])
        jacobs.append(jacobs_batch.reshape(jacobs_batch.size(0), -1).cpu().numpy())
    jacobs  = np.concatenate(jacobs,  axis=0)
    targets = targets.detach().cpu().numpy()

    try:
        jacob_cor_score = eval_score(jacobs, targets)
    except Exception as e:
        print(e)
        jacob_cor_score = np.nan

    return jacob_cor_score
