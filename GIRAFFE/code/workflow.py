#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.io as io
import nipype.interfaces.fsl as fsl

#Generic datagrabber module that wraps around glob in an
my_io_S3DataGrabber = pe.Node(io.S3DataGrabber(outfields=["func, anat"]), name = 'my_io_S3DataGrabber')
my_io_S3DataGrabber.inputs.bucket = 'openneuro'
my_io_S3DataGrabber.inputs.sort_filelist = True
my_io_S3DataGrabber.inputs.template = 'sub-01/(anat|func)/sub-01_(.*run-0?1_bold|T1w).nii.gz'
my_io_S3DataGrabber.inputs.anon = True
my_io_S3DataGrabber.inputs.bucket_path = 'ds000101/ds000101_R2.0.0/uncompressed/'
my_io_S3DataGrabber.inputs.local_directory = '/tmp'

#Wraps command **bet**
my_fsl_BET = pe.Node(interface = fsl.BET(), name='my_fsl_BET', iterfield = [''])

#Generic datasink module to store structured outputs
my_io_DataSink = pe.Node(interface = io.DataSink(), name='my_io_DataSink', iterfield = [''])
my_io_DataSink.inputs.base_directory = '/tmp'

#Wraps command **epi_reg**
my_fsl_EpiReg = pe.Node(interface = fsl.EpiReg(), name='my_fsl_EpiReg', iterfield = [''])

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(my_io_S3DataGrabber, "anat", my_fsl_BET, "in_file")
analysisflow.connect(my_io_S3DataGrabber, "func", my_fsl_EpiReg, "epi")
analysisflow.connect(my_fsl_BET, "out_file", my_fsl_EpiReg, "t1_brain")
analysisflow.connect(my_io_S3DataGrabber, "anat", my_fsl_EpiReg, "t1_head")
analysisflow.connect(my_fsl_EpiReg, "out_file", my_io_DataSink, "registered")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
