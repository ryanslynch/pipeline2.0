################################################################
# Basic parameters
################################################################
institution = "McGill"
pipeline = "PRESTO"
survey = "PALFA2.0"

################################################################
# Configurations for processing
################################################################
base_results_directory = "/data/data7/PALFA/test_new_pipeline_clean/"
base_working_directory = "/exports/scratch/PALFA/"
default_zaplist = "/homes/borgii/plazar/research/PALFA/pipeline2.0/lib/zaplists/PALFA.zaplist"
zaplistdir = "/homes/borgii/plazar/research/PALFA/pipeline2.0/lib/zaplists/"
log_dir = "/homes/borgii/plazar/research/PALFA/pipeline2.0_clean/pipeline2.0/log/"
log_archive = "/homes/borgii/plazar/research/PALFA/pipeline2.0_clean/pipeline2.0/log_archive/"
#log_dir = "C:/Reposotories/PALFA/pipeline2.0/log"
#log_archive = "C:/Reposotories/PALFA/pipeline2.0/log_archive"

max_jobs_running = 50
job_basename = "%s_batchjob" % survey
sleep_time = 10*60 # time to sleep between submitting jobs (in seconds)
max_attempts = 2 # Maximum number of times a job is attempted due to errors
#resource_list = "nodes=borg94:ppn=1:JumboFrame" # resource list for PBS's qsub
resource_list = "nodes=P248:ppn=1" # resource list for PBS's qsub
delete_rawdata = True
################################################################
# Configurations for raw data
################################################################
#rawdata_directory = "/data/alfa/FTP"
rawdata_directory = "/data/alfa/test_pipeline_clean/"
#rawdata_directory = "C:/Reposotories/PALFA/FTP"
rawdata_re_pattern = r"^p2030.*b[0-7]s[0-1]g?.*\.fits$"

################################################################
# Import presto_search module and set parameters
################################################################
def init_presto_search():
    """Import search module and set parameters.
        Return Module object that contains search's main function.
        The main function should have the following signature:
            main(filename, working_directory)
    """
    import PALFA2_presto_search as presto_search
    
    # The following determines if we'll dedisperse and fold using subbands.
    # In general, it is a very good idea to use them if there is enough scratch
    # space on the machines that are processing (~30GB/beam processed)
    presto_search.use_subbands          = True
    # To fold from raw data (ie not from subbands or dedispersed FITS files)
    # set the following to True.
    presto_search.fold_rawdata          = True
    
    # Tunable parameters for searching and folding
    # (you probably don't need to tune any of them)
    presto_search.datatype_flag           = "-psrfits" # PRESTO flag to determine data type
    presto_search.rfifind_chunk_time      = 2**15 * 0.000064  # ~2.1 sec for dt = 64us
    presto_search.singlepulse_threshold   = 5.0  # threshold SNR for candidate determination
    presto_search.singlepulse_plot_SNR    = 6.0  # threshold SNR for singlepulse plot
    presto_search.singlepulse_maxwidth    = 0.1  # max pulse width in seconds
    presto_search.to_prepfold_sigma       = 6.0  # incoherent sum significance to fold candidates
    presto_search.max_cands_to_fold       = 50   # Never fold more than this many candidates
    presto_search.numhits_to_fold         = 2    # Number of DMs with a detection needed to fold
    presto_search.low_DM_cutoff           = 2.0  # Lowest DM to consider as a "real" pulsar
    presto_search.lo_accel_numharm        = 16   # max harmonics
    presto_search.lo_accel_sigma          = 2.0  # threshold gaussian significance
    presto_search.lo_accel_zmax           = 0    # bins
    presto_search.lo_accel_flo            = 2.0  # Hz
    presto_search.hi_accel_numharm        = 8    # max harmonics
    presto_search.hi_accel_sigma          = 3.0  # threshold gaussian significance
    presto_search.hi_accel_zmax           = 50   # bins
    presto_search.hi_accel_flo            = 1.0  # Hz
    presto_search.low_T_to_search         = 20.0 # sec

    # DDplan configurations
    # The following configurations are for calculating dedispersion plans 
    # on demand. Currently dedispersion plans for WAPP and Mock data 
    # are hardcoded.
    # presto_search.lodm        = 0      # pc cm-3
    # presto_search.hidm        = 1000   # pc cm-3
    # presto_search.resolution  = 0.1    # ms
    # if presto_search.use_subbands:
    #     presto_search.numsub  = 96     # subbands
    # else:
    #     presto_search.numsub  = 0      # Defaults to number of channels

    # Sifting specific parameters (don't touch without good reason!)
    presto_search.sifting.sigma_threshold = presto_search.to_prepfold_sigma-1.0  
                                                   # incoherent power threshold (sigma)
    presto_search.sifting.c_pow_threshold = 100.0  # coherent power threshold
    presto_search.sifting.r_err           = 1.1    # Fourier bin tolerence for candidate equivalence
    presto_search.sifting.short_period    = 0.0005 # Shortest period candidates to consider (s)
    presto_search.sifting.long_period     = 15.0   # Longest period candidates to consider (s)
    presto_search.sifting.harm_pow_cutoff = 8.0    # Power required in at least one harmonic

    return presto_search


################################################################
# Downloader Configuration
#
# Downlaoder uses 'rawdata_directory' to move downlaoded files to
################################################################

downloader_api_service_url = "http://arecibo.tc.cornell.edu/palfadataapi/dataflow.asmx?WSDL"
downloader_api_username = "mcgill"
downloader_api_password = "palfa@Mc61!!"
#downloader_temp = "/data/alfa/test_pipeline" # When set to empty string will download to directory of the script
downloader_temp = "/data/alfa/test_pipeline_clean/" # When set to empty string will download to directory of the script
downloader_space_to_use = 228748364800#214748364800 #Size to use in bytes; Use 'None' to use all available space
downloader_numofdownloads = 2
downloader_numofrestores = 2
downloader_numofretries = 3

################################################################
# Result Uploader Configuration
#
# 
################################################################
uploader_result_dir_overide = True
uploader_result_dir = "/data/data7/PALFA/test_new_pipeline_clean/"
uploader_version_num = 'PRESTO:56b00442679f3c3edc36cbe322b2022eca53e459;PIPELINE:8512aac773bc1414f1dddd93397ca4aa5bb693a2'

################################################################
# Mailer Configuration
#
# Mailer uses following configurations to send notification email
# in case of an error.
################################################################
#!!!!!!!! Configure mailer in non versioned file: mail.cfg.py


################################################################
# Background Script Configuration
################################################################
bgs_sleep = 60 #sleep time for background script in seconds
bgs_screen_output = True #Set to True if you want the script to output runtime information, False otherwise
bgs_db_file_path = '/data/alfa/test_pipeline_clean/storage_db' #path to sqlite3 database file, put just the filename if the file is in the same directory as the background script
email_on_failures = True
email_on_terminal_failures = True

from sanity_check import SanityCheck

sanity = SanityCheck()
sanity.run()
