# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
#import tractor.api.author as author
import re
import os
from parameter.core import Parameter
from collections import OrderedDict

class TaskFfmpeg(TaskBase):

    codecs = OrderedDict(
        [
            ('ProRes422 HQ',{'flag':"prores -profile:v 3"}),
            ('ProRes422',{'flag': "prores -profile:v 2"}),
            ('ProRes422 LT',{'flag': "prores -profile:v 1"}),
            ('ProRes422 PROXY',{'flag': "prores -profile:v 0"}),
            ('h.264',{'flag':'libx264'})
        ]
    )


    def __init__(self):
        super(TaskFfmpeg,self).__init__()
        self.taskType = 'ffmpeg'
        self.title = 'ffmpeg task'
        self.frameRate = Parameter('29.97',widget='combobox',items=['29.97','59.94','30','60'])
        self.vcodec = Parameter('ProRes422 HQ',widget='combobox',items=TaskFfmpeg.codecs.keys())
        self.autoFrameRange = Parameter(True,widget='checkbox')
        self.oFileName = Parameter('',widget='file')

        self.service = []
        self.dPool = ''
        self.dGroup = ''

        self.param('fileName').alias = 'one of sequence'
        self.setVisible('serialSubTasks',False)
        self.setVisible('taskSize',False)

    def getReplacedFileName(self,fileName):
        dir = os.path.dirname(self.fileName)
        baseName, ext = os.path.splitext(self.fileName)
        # 拡張子なしファイル名抽出
        baseNameFirst, extFirst = os.path.splitext(os.path.basename(self.fileName))
        digit = re.findall(r'\d+$', baseNameFirst)
        if len(digit) > 0:
            digit = digit[0]
        else:
            dutil.logError('invalid file name. ' + self.fileName)
            return None

        number = int(digit)
        numDigit = len(digit)
        baseNameWithoutNumber = baseNameFirst.strip(digit)

        replacedFileName = dir + '/' + baseNameWithoutNumber + r'%' + str(numDigit) + 'd' + ext

        return replacedFileName,number

    def makeFfMpegCommnad(self):

        bin = "ffmpeg.exe"
        startNumber = -1
        iFileName = ''
        ext = ''

        if self.autoFrameRange:
            if not os.path.exists(self.fileName):
                return None

            dir = os.path.dirname(self.fileName)
            baseName, ext = os.path.splitext(self.fileName)

            files = []
            for filename in os.listdir(dir):
                if os.path.isfile(os.path.join(dir, filename)):
                    files.append(dir + '/' + filename)

            imagefiles = []
            regStr = str(ext + r'$')
            regex = re.compile(regStr)
            for name in files:
                if regex.search(name):
                    imagefiles.append(name)

            imagefiles.sort()
            firstImage = imagefiles[0]

            iFileName,startNumber = self.getReplacedFileName(firstImage)
        else:
            iFileName,number = self.getReplacedFileName(self.fileName)
            startNumber = self.start
            baseName, ext = os.path.splitext(self.fileName)

        cmd = [bin,
               '-start_number', str(startNumber),
               '-y',
               '-r', str(self.frameRate),
               '-i', iFileName,
               self.oFileName]

        if not self.autoFrameRange:
            vframes = self.end - self.start + 1
            vframesOption = ['-vframes',str(int(vframes))]
            insert = len(cmd) - 1
            cmd[insert:insert] = vframesOption

        vcodecArg = ['-vcodec'] + TaskFfmpeg.codecs[self.vcodec]['flag'].split(' ')
        insert = len(cmd) - 1
        cmd[insert:insert] = vcodecArg

        if ext == '.exr':
            inputImageOption = ['-vf', 'lutrgb=r=gammaval(0.45454545):g=gammaval(0.45454545):b=gammaval(0.45454545)']
            insert = len(cmd) - 1
            cmd[insert:insert] = inputImageOption

        return cmd

    def makeTask(self):

        cmd = self.makeFfMpegCommnad()

        trTask = author.Task()
        trTask.title = self.title

        trCommand = author.Command()
        trCommand.argv = cmd
        trCommand.tags = self.tags
        trCommand.service = self.getServiceAsTractorFormat()
        trTask.addCommand(trCommand)

        return trTask



    def makeOption(self):

        startNumber = -1
        iFileName = ''
        ext = ''

        if self.autoFrameRange:
            if not os.path.exists(self.fileName):
                return None

            dir = os.path.dirname(self.fileName)
            baseName, ext = os.path.splitext(self.fileName)

            files = []
            for filename in os.listdir(dir):
                if os.path.isfile(os.path.join(dir, filename)):
                    files.append(dir + '/' + filename)

            imagefiles = []
            regStr = str(ext + r'$')
            regex = re.compile(regStr)
            for name in files:
                if regex.search(name):
                    imagefiles.append(name)

            imagefiles.sort()
            firstImage = imagefiles[0]

            iFileName, startNumber = self.getReplacedFileName(firstImage)
        else:
            iFileName, number = self.getReplacedFileName(self.fileName)
            startNumber = self.start
            baseName, ext = os.path.splitext(self.fileName)

        inputOption = ['-start_number', str(startNumber),
                       '-y',
                       '-r', str(self.frameRate),
                       ]

        outputOption = []

        if not self.autoFrameRange:
            vframes = self.end - self.start + 1
            vframesOption = ['-vframes', str(int(vframes))]
            outputOption.extend(vframesOption)

        vcodecArg = ['-vcodec'] + TaskFfmpeg.codecs[self.vcodec]['flag'].split(' ')
        outputOption += vcodecArg
        outputOption += ['-c:v','prores_ks']
        outputOption += ['-vf','scale=out_color_matrix=bt709','-movflags','write_colr','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
        # outputOption += ['-vendor','ap10','-pix_fmt','yuv422p10le','-qscale','2']

        #not working
        # outputOption += ['-vf','zscale=matrixin=709:matrix=709:transferin=709:transfer=709:primariesin=709:primaries=709']
        # outputOption += ['-bsf:v','prores_metadata=color_primaries=bt709:color_trc=bt709:colorspace=bt709']


        if ext == '.exr':
            outputOption += ['-vf', 'lutrgb=r=gammaval(0.45454545):g=gammaval(0.45454545):b=gammaval(0.45454545)']

        inputOption = ' '.join(inputOption)
        outputOption = ' '.join(outputOption)

        # outputOption += ' -vf scale=out_color_matrix=bt709 -movflags write_colr -color_primaries bt709 -color_trc bt709 -colorspace bt709'

        return inputOption,outputOption,iFileName

    # def dlMakeTask(self, batchInfo):
    #
    #     self.dGroup = 'elite'#fource override
    #
    #     jobInfo = self.dlSetupJobInfo('CommandLine', batchInfo)
    #     jobInfo.Frames = ''
    #
    #
    #     cmd = self.makeFfMpegCommnad()
    #     executable = cmd.pop(0)
    #     option = ' '.join(cmd)
    #     singleFramesOnly = True
    #
    #     pluginInfo = {
    #         'Shell': 'default',
    #         'ShellExecute': False,
    #         'StartupDirectory': '',
    #         'Executable': executable,
    #         'Arguments': option,
    #         'SingleFramesOnly': singleFramesOnly
    #     }
    #
    #     new_job = self.dlSubmit(jobInfo, pluginInfo)
    #     return new_job

    def dlMakeTask(self, batchInfo):

        # self.dGroup = 'elite'#fource override

        jobInfo = self.dlSetupJobInfo('FFmpeg', batchInfo)
        jobInfo.Frames = ''

        inputOption,outputOption,iFileName = self.makeOption()

        pluginInfo = {
            'InputFile0':iFileName,
            'InputArgs0':inputOption,
            'ReplacePadding0':False,
            'OutputFile':self.oFileName,
            'OutputArgs':outputOption
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job


