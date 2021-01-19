
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


def generate_from_file(queue, file_path, encoding, found):
	with open(file_path, encoding=encoding) as f:
		for word in f:
			queue.put(word.strip())
			if found.value:
				return


def generate_brute_force(queue, found, char_list, min_len=6, max_len=12):
	for length in range(min_len, max_len+1):
		for word in itertools.product(char_list, repeat=length):
			queue.put(''.join(word))
			if found.value:
				return


def test(queue, md5_hash, counter, found):
	while queue and not found.value:
		word = queue.get()
		h = hashlib.md5(word.encode()).hexdigest()
		if h == md5_hash:
			print(f'\nFound password: {word}')
			found.value = 1
		counter.value += 1



def brute_force(md5_hash, char_list, min_len, max_len, found):

	def calculate_total_possibilities(char_list, min_len, max_len):
		total = 0
		char_count = len(char_list)
		for i in range(min_len, max_len+1):
			total += char_count ** i
		return total

	counter = mp.Value('i', 0)
	queue = mp.Queue(maxsize=1000)
	total_combinations = calculate_total_possibilities(char_list, min_len, max_len)

	start = time.time()
	pool = mp.Pool(None, test, (queue, md5_hash, counter, found))
	generator = mp.Process(target=generate_brute_force, args=(queue, found, char_list, min_len, max_len))
	generator.start()

	while True:
		percentage = counter.value / total_combinations * 100
		speed = counter.value/(time.time()-start)
		eta = format_time((total_combinations - counter.value) / speed) if speed > 0 else 'N/A'
		print(f'\rWords tried: {counter.value}/{total_combinations} ({percentage:.02f}%); {speed:.02f} wps; ETA: {eta}', end='')
		time.sleep(1)
		if found.value or not queue:
			break

	generator.join()
	if not found.value:
		print('\nNo match found.')



def try_known_passwords(md5_hash, file_path, encoding, found):
	counter = mp.Value('i', 0)
	queue = mp.Queue(maxsize=1000)
	total_lines = 0
	with open(file_path, encoding=encoding) as f:
		for _ in f:
			total_lines += 1

	start = time.time()
	pool = mp.Pool(None, test, (queue, md5_hash, counter, found))
	generator = mp.Process(target=generate_from_file, args=(queue, file_path, encoding, found))
	generator.start()

	while True:
		percentage = counter.value / total_lines * 100
		speed = counter.value/(time.time()-start)
		eta = format_time((total_lines - counter.value) / speed) if speed > 0 else 'N/A'
		print(f'\rWords tried: {counter.value}/{total_lines} ({percentage:.02f}%); {speed:.02f} wps; ETA: {eta}', end='')
		time.sleep(1)
		if found.value:
			break

	generator.join()
	if not found.value:
		print('\nNo match in known passwords.')


def main(args):
	found = mp.Value('b', 0)
	if args.password_file:
		print('Trying known passwords...')
		try_known_passwords(args.hash, args.password_file, args.encoding, found)
	if not found.value:
		print(f'Trying all combinations of length between {args.min_len} and {args.max_len}...')
		brute_force(args.hash, args.char_list, args.min_len, args.max_len, found)



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('hash', type=str)
	parser.add_argument('--password_file', type=str)
	parser.add_argument('--encoding', type=str, default='utf-8')
	parser.add_argument('--min_len', type=int, default=6)
	parser.add_argument('--max_len', type=int, default=12)
	parser.add_argument('--char_list', type=str, default=string.printable[:-4])
	main(parser.parse_args())