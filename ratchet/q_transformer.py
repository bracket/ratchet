import numpy as np

class QTransformer(object):
    def __init__(
        self, sample_rate, min_frequency,
        max_frequency=None, fft_buckets=4096, resolution_in_cents=50,
        kernel_threshold = .05,
    ):
        from math import log

        self.sample_rate = sample_rate
        self.min_frequency = min_frequency

        if max_frequency is None:
            max_frequency = sample_rate / 2

        self.max_frequency = max_frequency

        self.fft_buckets = fft_buckets
        self.resolution_in_cents = resolution_in_cents

        self.kernel_threshold = kernel_threshold

        log_min = log(min_frequency, 2)
        log_max = log(max_frequency, 2)
        log_delta = resolution_in_cents / 1200

        self.frequencies = 2 ** np.arange(log_min, log_max, log_delta)
        self.sparse_kernels = [ self.sparse_kernel(f) for f in self.frequencies ]


    def transform(self, sample):
        sample = self.resize_sample(sample)
        fft = np.fft.rfft(sample)

        return np.array([ np.dot(fft[s], k) for s, k in self.sparse_kernels ])


    def bucket_frequency(self, k):
        return self.min_frequency * (2 ** (k * self.resolution_in_cents / 1200))


    def window_length(self, frequency):
        from math import ceil

        Q = int(1 / ((2 ** (self.resolution_in_cents / 1200)) - 1))

        return int(ceil(self.sample_rate * Q / frequency))


    def window(self, window_length, alpha=25/46):
        from math import pi

        if window_length > self.fft_buckets:
            window_length = self.fft_buckets

        ordinates = np.linspace(0., 2 * pi, window_length, endpoint=True)
        window = (1 - alpha) * (-np.cos(ordinates)) + alpha

        return self.resize_sample(window)


    def temporal_kernel(self, frequency):
        from math import pi

        radians = pi * (frequency / self.sample_rate) * self.fft_buckets
        ordinates = np.linspace(-radians, radians, self.fft_buckets, endpoint=False)

        window_length = self.window_length(frequency)

        kernel = self.window(window_length) * np.cos(ordinates)
        kernel *= (self.fft_buckets / np.sum(np.abs(kernel)))

        return kernel


    def spectral_kernel(self, frequency):
        return np.conj(np.fft.rfft(self.temporal_kernel(frequency))) / self.fft_buckets


    def sparse_kernel(self, frequency):
        kernel = np.real(self.spectral_kernel(frequency))
        indices = np.where(np.abs(kernel) > self.kernel_threshold)

        start = np.min(indices)
        end = np.max(indices) + 1

        s = slice(start, end)
        kernel = kernel[s].copy()

        return s, kernel


    def resize_sample(self, sample, length=None):
        if length is None:
            length = self.fft_buckets

        if len(sample) >= length:
            return sample[-length:]

        pad = (length - len(sample))
        before = round(pad/2)
        after = pad - before

        return np.pad(sample, [(before, after)], 'constant')
