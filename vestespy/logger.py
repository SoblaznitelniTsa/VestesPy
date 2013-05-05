# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from vestespy import colorama
colorama.init()

class Console:

	def log(self, *args, **kwargs):
		head = kwargs.pop("head", None)
		head_color = kwargs.pop("color", "").upper()
		head_style = kwargs.pop("style", "").upper()
		pre = kwargs.pop("pre", colorama.Fore.WHITE + colorama.Style.NORMAL)

		args = [str(arg) for arg in args]
		args[0] = pre + args[0]
		args[len(args)-1] += colorama.Style.RESET_ALL
		if head:
			color = getattr(colorama.Fore, head_color, colorama.Fore.YELLOW)
			style = getattr(colorama.Style, head_style, colorama.Style.BRIGHT)
			args.insert(0, color+style+head)

		print(*args, **kwargs)
		sys.stdout.flush()

	def info(self, *args, **kwargs):
		kwargs["head"] = "[INFO]"
		kwargs["color"] = "black"
		self.log(*args, **kwargs)

	def error(self, *args, **kwargs):
		kwargs["head"] = "[ERROR]"
		kwargs["color"] = "red"
		kwargs["pre"] = colorama.Fore.WHITE + colorama.Style.BRIGHT
		self.log(*args, **kwargs)

	def warn(self, *args, **kwargs):
		kwargs["head"] = "[WARNING]"
		kwargs["color"] = "cyan"
		self.log(*args, **kwargs)

	def success(self, *args, **kwargs):
		kwargs["head"] = "[SUCCESS]"
		kwargs["color"] = "green"
		self.log(*args, **kwargs)