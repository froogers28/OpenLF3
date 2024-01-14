#!/usr/bin/env python
##############################################################################
#    OpenLFConnect
#
#    Copyright (c) 2012 Jason Pruitt <jrspruitt@gmail.com>
#
#    This file is part of OpenLFConnect.
#    OpenLFConnect is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenLFConnect is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenLFConnect.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################



##############################################################################
# Title:   OpenLFConnect
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
# firmware/images.py Version 0.5
import os
import re
import configparser
from subprocess import Popen, PIPE
from shlex import split as shlex_split

class jffs2(object):
    def __init__(self):
        self._mount = '/mnt/jffs2_leapfrog'
        self._modprobe = 'sudo /sbin/modprobe'


    def error(self, e):
        assert False, e



    def popen(self, cmd):
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            err = p.stderr.read()
            out = p.stdout.read()
            return [out, err]
        except Exception as e:
            self.error(e)


    def popen_arr(self, cmds):
        try:
            ret_arr = []
            for cmd in cmds:
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                err = p.stderr.read()
                out = p.stdout.read()
                ret_arr.append([cmd, out, err])
            return ret_arr         
        except Exception as e:
            self.error(e)



                       
    def mount(self, path):
        try:
            if not os.path.exists(path):
                self.error('Image path does not exist.')

            if not path.endswith('.jffs2'):
                self.error('Path does not look like a jffs2 file.')
            
            if os.path.exists(self._mount):
                self.error('Looks like a jffs2 image is already mounted.')

            proc_mtd = '/proc/mtd'
            proc_mtd_regex = r'^mtd(?P<mnum>[\d]{1})'
            mtd_num = None

            if not os.path.exists(self._mount):
                self.popen(shlex_split('sudo mkdir %s' % self._mount))

            cmd_mtdram = shlex_split('%s mtdram total_size=16384 erase_size=128' % self._modprobe)
            cmd_mtdblock = shlex_split('%s mtdblock' % self._modprobe)
            cmd_jffs2 = shlex_split('%s jffs2' % self._modprobe)
            cmds = [cmd_mtdram, cmd_mtdblock, cmd_jffs2]
            self.popen_arr(cmds)

            if os.path.exists(proc_mtd):
                f = open(proc_mtd, 'r')
                for line in f:
                    if 'mtdram' in line:
                        mtdr = re.compile(proc_mtd_regex)
                        mtds = mtdr.search(line)
                        break
                    
                f.close()
                if mtds:
                    mtd_num = mtds.group('mnum')
                else:
                    self.error('Could not determine mtd number.')

            cmd_dd = shlex_split('sudo dd if=%s of=/dev/mtdblock%s' % (path, mtd_num))
            cmd_mount = shlex_split('sudo /bin/mount -t jffs2 /dev/mtdblock%s %s -o rw,noatime,nodiratime,users' % (mtd_num, self._mount))
            cmds = [cmd_dd, cmd_mount]
            self.popen_arr(cmds)

            print('Mounted at: %s' % self._mount)

        except Exception as e:
            self.error(e)



    def umount(self):
        try:
            cmd_umount = shlex_split('sudo /bin/umount %s' % self._mount)
            cmd_rmmod = shlex_split("sudo /sbin/rmmod jffs2 mtdblock mtdram")
            cmds = [cmd_umount, cmd_rmmod]
            self.popen_arr(cmds)

            if os.path.exists(self._mount):
                self.popen(shlex_split('sudo rmdir %s' % self._mount))
        except Exception as e:
            self.error(e)



    def create(self, opath, ipath):
        try:
            if not os.path.isdir(ipath):
                self.error('Input path is not a directory.')
            
            if not opath.endswith('.jffs2'):
                opath = '%s.jffs2' % opath

            cmd_mkjffs2 = shlex_split('sudo mkfs.jffs2 -p -r %s -e 128 -o %s' % (ipath, opath))
            cmd_chmod = shlex_split('sudo chmod 777 %s' % opath)
            cmds = [cmd_mkjffs2, cmd_chmod]
            self.popen_arr(cmds)
        except Exception as e:
            self.error(e)



class ubi(object):
    def __init__(self, ubi_version='0'):
        self._mount = '/mnt/ubi_leapfrog'
        self._modprobe = 'sudo /sbin/modprobe'
        self._ubi_loc = 'sudo /usr/sbin/'
        self._ubi_version = ubi_version
        self._force_4096 = ''
        self._app_path = os.path.dirname(os.path.dirname(__file__))
        self._params = {}
        if ubi_version > 0:
            self._cfg = configparser.ConfigParser()
            self._cfg.readfp(open(os.path.join(self._app_path, 'firmware/ubi_cfg/params.cfg'), 'r'))
            self.get_ubi_params()

    def error(self, e):
        assert False, e


    def get_ubi_params(self):
        params = ['leb_size',
                  'max_leb_cnt',
                  'min_io_size',
                  'peb_size',
                  'sub_page_size',
                  'vid_hdr_offset']

        for param in params:
            self._params[param] = self._cfg.get(self._ubi_version, param)


    def popen(self, cmd):
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            err = p.stderr.read()
            out = p.stdout.read()
            return [out, err]
        except Exception as e:
            self.error(e)


    def popen_arr(self, cmds):
        try:
            ret_arr = []
            for cmd in cmds:
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                err = p.stderr.read()
                out = p.stdout.read()
                ret_arr.append([cmd, out, err])
            return ret_arr         
        except Exception as e:
            self.error(e)


        
    def mount(self, path):
        try:
            if not os.path.exists(path):
                self.error('Image path does not exist.')

            if not path.endswith('.ubi'):
                self.error('Path does not look like an Explorer UBI file.')
            
            if os.path.exists(self._mount):
                self.error('Looks like a ubi image is already mounted.')

            proc_mtd = '/proc/mtd'
            proc_mtd_regex = r'^mtd(?P<mnum>[\d]{1})'
            mtd_num = None
            ubiattach_regex = r'^UBI device number (?P<unum>[\d]{1})'
            ubi_num = None

            if not os.path.exists(self._mount):
                self.popen(shlex_split('sudo mkdir %s' % self._mount)) 

            if self._ubi_version == '1':
	            cmd_nandsim = shlex_split('%s nandsim first_id_byte=0x2C second_id_byte=0xDC third_id_byte=0x00 fourth_id_byte=0x15' % self._modprobe)
            elif self._ubi_version == '2':
                cmd_nandsim = shlex_split('%s nandsim first_id_byte=0x2c second_id_byte=0x68 third_id_byte=0x04 fourth_id_byte=0x4A cache_file=/tmp/nandsim_cache' % self._modprobe)
                self._force_4096 = '-O 4096'

            self.popen(cmd_nandsim)
            
            if os.path.exists(proc_mtd):
                f = open(proc_mtd, 'r')
                for line in f:
                    if 'NAND' in line:
                        mtdr = re.compile(proc_mtd_regex)
                        mtds = mtdr.search(line)
                        break
                    
                f.close()
                if mtds:
                    mtd_num = mtds.group('mnum')
                else:
                    self.error('Could not determine mtd number.')                
            else:
                self.error('mtd not created.')

            cmd_ubi = shlex_split('%s ubi mtd=%s' % (self._modprobe, mtd_num))
            cmd_ubidetach = shlex_split('%subidetach /dev/ubi_ctrl -m %s' % (self._ubi_loc, mtd_num)) 
            self.popen_arr([cmd_ubi, cmd_ubidetach])
            cmd_ubiformat = shlex_split('%subiformat -e 1 %s /dev/mtd%s -f %s' % (self._ubi_loc, self._force_4096, mtd_num, path))           

            p = Popen(cmd_ubiformat, stdin=PIPE, stdout=PIPE, stderr=PIPE)

            if self._ubi_version == '2':
                p.stdin.write('y\n')

            ufout = p.stdout.read()
            uferr = p.stderr.read()

            if 'first detach mtd' in uferr:
                self.error('Another image is already mounted')

            cmd_ubiattach = shlex_split('%subiattach /dev/ubi_ctrl -m %s %s' % (self._ubi_loc, mtd_num, self._force_4096))
            uout = self.popen(cmd_ubiattach)[0]
            ubir = re.compile(ubiattach_regex)
            ubis = ubir.search(uout)

            if ubis:
                ubi_num = ubis.group('unum')
            else:
                self.error('Could not determine ubi number.')
            
            cmd_mount = shlex_split('sudo /bin/mount -t ubifs ubi%s %s -o rw,noatime,nodiratime,users' % (ubi_num, self._mount))
            self.popen(cmd_mount)

            print('Mounted at: %s' % self._mount)
                
        except Exception as e:
            if os.path.exists(self._mount):
                self.popen(shlex_split('sudo rmdir %s' % self._mount))
            self.error(e)



    def umount(self):
        try:
            cmd_umount = shlex_split('sudo /bin/umount %s' % self._mount)
            cmd_rmmod = shlex_split('sudo /sbin/rmmod ubifs ubi nandsim')
            cmds = [cmd_umount, cmd_rmmod]
            self.popen_arr(cmds)
            
            if os.path.exists(self._mount):
                self.popen(shlex_split('sudo rmdir %s' % self._mount))       
        except Exception as e:
            self.error(e)



    def create(self, part, opath, ipath):
        try:
            if not opath.endswith('.ubi'):
                opath = '%s.ubi' % opath
                
            if not os.path.isdir(ipath):
                self.error('Input path is not a directory.')

            if part.lower() == 'erootfs':
                ini_file = os.path.join(self._app_path, 'firmware/ubi_cfg/%serootfs.ini' % self._ubi_version)
            elif part.lower() == 'bulk':
                ini_file = os.path.join(self._app_path, 'firmware/ubi_cfg/%sbulk.ini' % self._ubi_version)
            else:
                self.error('Partion must be erootfs, or bulk.')

            mkfs = '-c %s -m %s -e %s -r %s' % (self._params['max_leb_cnt'],
                                                self._params['min_io_size'],
                                                self._params['leb_size'],
                                                ipath)

            ubinz = '-o %s -p %s -m %s -s %s -O %s %s' % (opath,
                                                          self._params['peb_size'],
                                                          self._params['min_io_size'],
                                                          self._params['sub_page_size'],
                                                          self._params['vid_hdr_offset'],
                                                          ini_file)

            cmd_mkubi = shlex_split('sudo /usr/sbin/mkfs.ubifs %s temp.ubifs' % (mkfs))        
            cmd_ubinize = shlex_split('sudo /usr/sbin/ubinize  %s' % (ubinz))
            cmd_rmimg = shlex_split('sudo rm temp.ubifs')
            cmd_chmod = shlex_split('sudo chmod 777 %s' % opath)
            cmds = [cmd_mkubi, cmd_ubinize, cmd_rmimg, cmd_chmod]
            self.popen_arr(cmds)
        except Exception as e:
            self.error(e)
                    
                    
