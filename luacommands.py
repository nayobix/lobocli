__author__ = "Boyan Vladinov"
__copyright__ = "Copyright 2016"
__license__ = "GPL"

MCU = {
	'ver': 'print(mcu.ver());\r\n',
	'info': 'print(mcu.info());\r\n',
	'reboot': 'mcu.reboot();\r\n',
	'mem': 'print(mcu.mem());\r\n',
	'chipid': 'print(mcu.chipid());\r\n',
	'sgetparams': 'print(mcu.sgetparams());\r\n',
    }

FILE = {
	'format': 'file.format()\n',
	'slist': 'print(file.slist());\r\n',
    }

FILE_ARG = {
	'read': """
		if (file.exists("%s") == true) then
			fh = file.open("%s", "r");
			if (fh ~= nil) then
				fname, fsize = file.state(fh);
				sizemod = math.floor(fsize/512);
				while (sizemod >= 0) do
					data = file.read(fh);
					print(data);
					sizemod = sizemod - 1;
				end;
				file.close(fh);
				data = nil;
				fh = nil;
			end;
		else
			print("File does not exist");
		end;
		""",
	'write_open': """
		fh = file.open("%s", "w+");
		""",
	'write_data': """
		file.writeline(fh, "%s");
		""",
	'write_close': """
		file.flush(fh)
		file.close(fh);
		fh = nil
		""",
    }
