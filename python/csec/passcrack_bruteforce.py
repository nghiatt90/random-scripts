
# Brute force password cracking demo

import argparse
import hashlib
import itertools
import multiprocessing as mp
import string
import time


def format_time(seconds):
	seconds = int(seconds)
	minutes = seconds // 60
	seconds %= 60
	hours = minutes // 60
	minutes %= 60
	days = hours // 24
	hours %= 24
	return f'{days}d {hours:02d}h {minutes:02d}m {seconds:02d}s'


def calculate_total_possibilities(char_list, min_len, max_len):
	total = 0
	char_count = len(char_list)
	for i in range(min_len, max_len+1):
		total += char_count ** i
	return total


def generate(queue, stop, char_list, min_len=6, max_len=12):
	for length in range(min_len, max_len+1):
		for word in itertools.product(char_list, repeat=length):
			queue.put(''.join(word))
			if stop.value:
				return


def test(queue, md5_hash, counter, stop):
	while queue and not stop.value:
		word = queue.get()
		h = hashlib.md5(word.encode()).hexdigest()
		if h == md5_hash:
			print(f'\nFound password: {word}')
			stop.value = 1
		counter.value += 1


def main(args):
	counter = mp.Value('i', 0)
	stop = mp.Value('b', 0)
	md5_hash = args.hash
	queue = mp.Queue(maxsize=1000)
	char_list = args.char_list
	total_combinations = calculate_total_possibilities(char_list, args.min_len, args.max_len)

	start = time.time()
	pool = mp.Pool(None, test, (queue, md5_hash, counter, stop))
	generator = mp.Process(target=generate, args=(queue, stop, char_list, args.min_len, args.max_len))
	generator.start()

	while True:
		percentage = counter.value / total_combinations * 100
		speed = counter.value/(time.time()-start)
		eta = format_time((total_combinations - counter.value) / speed) if speed > 0 else 'N/A'
		print(f'\rWords tried: {counter.value}/{total_combinations} ({percentage:.02f}%); {speed:.02f} wps; ETA: {eta}', end='')
		time.sleep(1)
		if stop.value:
			break

	generator.join()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('hash', type=str)
	parser.add_argument('--min_len', type=int, default=6)
	parser.add_argument('--max_len', type=int, default=12)
	parser.add_argument('--char_list', type=str, default=string.printable[:-4])
	main(parser.parse_args())