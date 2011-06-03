#!/usr/bin/env python

"""
Header object for uploading datafile information to commonDB from 
    a given PALFA data file.

Patrick Lazarus, Jan. 5, 2011
"""

import os.path
import sys
import re
import warnings
import types
import optparse

import upload
import datafile
import database
import pipeline_utils

# Raise warnings produced by invalid coord strings as exceptions
warnings.filterwarnings("error", message="Input is not a valid sexigesimal string: .*")

class Header(upload.Uploadable):
    """PALFA Header object. 
    """
    def __init__(self, datafns, *args, **kwargs):
        if isinstance(datafns, datafile.Data):
            self.data = datafns
        else:
            self.data = datafile.autogen_dataobj(datafns, *args, **kwargs)
        
        # List of dependents (ie other uploadables that require 
        # the header_id from this header)
        self.dependents = []

    def add_dependent(self, dep):
        self.dependents.append(dep)
    
    def upload(self, dbname, *args, **kwargs):
        """An extension to the inherited 'upload' method.
            This method will make sure any dependents have
            the header_id and then upload them.

            Input:
                dbname: Name of database to connect to, or a database
                        connection to use (Defaut: 'default').
        """
        header_id = super(Header, self).upload(dbname=dbname, *args, **kwargs)[0]
        if not self.compare_with_db(dbname=dbname):
            raise HeaderError("Header doesn't " \
                    "match what was uploaded to DB!")
        for dep in self.dependents:
            dep.header_id = header_id
            dep.upload(dbname=dbname, *args, **kwargs)
        return header_id

    def __getattr__(self, key):
        # Allow Header object to return Data object's attributes
        return getattr(self.data, key)

    def get_upload_sproc_call(self):
        """Return the EXEC spHeaderLoader string to upload
            this header to the PALFA common DB.
        """
        sprocstr = "EXEC spHeaderLoader " + \
            "@obs_name='%s', " % self.obs_name + \
            "@beam_id=%d, " % self.beam_id + \
            "@original_wapp_file='%s', " % self.original_file + \
            "@sample_time=%f, " % self.sample_time + \
            "@observation_time=%f, " % self.observation_time + \
            "@timestamp_mjd=%.15f, " % self.timestamp_mjd + \
            "@num_samples_per_record=%d, " % self.num_samples_per_record + \
            "@center_freq=%f, " % self.center_freq + \
            "@channel_bandwidth=%f, " % self.channel_bandwidth + \
            "@num_channels_per_record=%d, " % self.num_channels_per_record + \
            "@num_ifs=%d, " % self.num_ifs + \
            "@orig_right_ascension=%.4f, " % self.orig_right_ascension + \
            "@orig_declination=%.4f, " % self.orig_declination + \
            "@orig_galactic_longitude=%.8f, " % self.orig_galactic_longitude + \
            "@orig_galactic_latitude=%.8f, " % self.orig_galactic_latitude + \
            "@source_name='%s', " % self.source_name + \
            "@sum_id=%d, " % self.sum_id + \
            "@orig_start_az=%.4f, " % self.orig_start_az + \
            "@orig_start_za=%.4f, " % self.orig_start_za + \
            "@start_ast=%.8f, " % self.start_ast + \
            "@start_lst=%.8f, " % self.start_lst + \
            "@project_id='%s', " % self.project_id + \
            "@observers='%s', " % self.observers + \
            "@file_size=%d, " % self.file_size + \
            "@data_size=%d, " % self.data_size + \
            "@num_samples=%d, " % self.num_samples + \
            "@orig_ra_deg=%.8f, " % self.orig_ra_deg + \
            "@orig_dec_deg=%.8f, " % self.orig_dec_deg + \
            "@right_ascension=%.4f, " % self.right_ascension + \
            "@declination=%.4f, " % self.declination + \
            "@galactic_longitude=%.8f, " % self.galactic_longitude + \
            "@galactic_latitude=%.8f, " % self.galactic_latitude + \
            "@ra_deg=%.8f, " % self.ra_deg + \
            "@dec_deg=%.8f, " % self.dec_deg + \
            "@obsType='%s'" % self.obstype
        return sprocstr

    def compare_with_db(self, dbname='default'):
        """Grab corresponding header from DB and compare values.
            Return True if all values match. Return False otherwise.

            Input:
                dbname: Name of database to connect to, or a database
                        connection to use (Defaut: 'default').
            Outputs:
                match: Boolean. True if all values match, False otherwise.
        """
        if isinstance(dbname, database.Database):
            db = dbname
        else:
            db = database.Database(dbname)
        db.execute("SELECT obs.obs_name, " \
                          "h.beam_id, " \
                          "h.original_wapp_file, " \
                          "h.sample_time, " \
                          "h.observation_time, " \
                          "h.timestamp_mjd, " \
                          "h.num_samples_per_record, " \
                          "h.center_freq, " \
                          "h.channel_bandwidth, " \
                          "h.num_channels_per_record, " \
                          "h.num_ifs, " \
                          "h.orig_right_ascension, " \
                          "h.orig_declination, " \
                          "h.orig_galactic_longitude, " \
                          "h.orig_galactic_latitude, " \
                          "h.source_name, " \
                          "h.sum_id, " \
                          "h.orig_start_az, " \
                          "h.orig_start_za, " \
                          "h.start_ast, " \
                          "h.start_lst, " \
                          "h.project_id, " \
                          "h.observers, " \
                          "h.file_size, " \
                          "h.data_size, " \
                          "h.num_samples, " \
                          "h.orig_ra_deg, " \
                          "h.orig_dec_deg, " \
                          "h.right_ascension, " \
                          "h.declination, " \
                          "h.galactic_longitude, " \
                          "h.galactic_latitude, " \
                          "h.ra_deg, " \
                          "h.dec_deg, " \
                          "h.obsType " \
                   "FROM headers AS h " \
                   "LEFT JOIN observations AS obs ON obs.obs_id=h.obs_id " \
                   "WHERE obs.obs_name='%s' AND h.beam_id=%d " % \
                        (self.obs_name, self.beam_id))
        rows = db.cursor.fetchall()
        if type(dbname) == types.StringType:
            db.close()
        if not rows:
            # No matching entry in common DB
            raise ValueError("No matching entry in common DB!\n" \
                                "(obs_name: %s, beam_id: %d)" % \
                                (self.obs_name, self.beam_id))
        elif len(rows) > 1:
            # Too many matching entries!
            raise ValueError("Too many matching entries in common DB!\n" \
                                "(obs_name: %s, beam_id: %d)" % \
                                (self.obs_name, self.beam_id))
        else:
            desc = [d[0] for d in db.cursor.description]
            r = dict(zip(desc, rows[0]))
            matches = [('%s' % r['obs_name'].lower() == '%s' % self.obs_name.lower()),  \
                     ('%d' % r['beam_id'] == '%d' % self.beam_id),  \
                     ('%s' % r['original_wapp_file'].lower() == '%s' % self.original_file.lower()),  \
                     ('%f' % r['sample_time'] == '%f' % self.sample_time),  \
                     ('%f' % r['observation_time'] == '%f' % self.observation_time),  \
                     ('%.15f' % r['timestamp_mjd'] == '%.15f' % self.timestamp_mjd),  \
                     ('%d' % r['num_samples_per_record'] == '%d' % self.num_samples_per_record),  \
                     ('%f' % r['center_freq'] == '%f' % self.center_freq),  \
                     ('%f' % r['channel_bandwidth'] == '%f' % self.channel_bandwidth),  \
                     ('%d' % r['num_channels_per_record'] == '%d' % self.num_channels_per_record),  \
                     ('%d' % r['num_ifs'] == '%d' % self.num_ifs),  \
                     ('%.4f' % r['orig_right_ascension'] == '%.4f' % self.orig_right_ascension),  \
                     ('%.4f' % r['orig_declination'] == '%.4f' % self.orig_declination),  \
                     ('%.8f' % r['orig_galactic_longitude'] == '%.8f' % self.orig_galactic_longitude),  \
                     ('%.8f' % r['orig_galactic_latitude'] == '%.8f' % self.orig_galactic_latitude),  \
                     ('%s' % r['source_name'].lower() == '%s' % self.source_name.lower()),  \
                     ('%d' % r['sum_id'] == '%d' % self.sum_id),  \
                     ('%.4f' % r['orig_start_az'] == '%.4f' % self.orig_start_az),  \
                     ('%.4f' % r['orig_start_za'] == '%.4f' % self.orig_start_za),  \
                     ('%.8f' % r['start_ast'] == '%.8f' % self.start_ast),  \
                     ('%.8f' % r['start_lst'] == '%.8f' % self.start_lst),  \
                     ('%s' % r['project_id'].lower() == '%s' % self.project_id.lower()),  \
                     ('%s' % r['observers'].lower() == '%s' % self.observers.lower()),  \
                     ('%d' % r['file_size'] == '%d' % self.file_size),  \
                     ('%d' % r['data_size'] == '%d' % self.data_size),  \
                     ('%d' % r['num_samples'] == '%d' % self.num_samples),  \
                     ('%.8f' % r['orig_ra_deg'] == '%.8f' % self.orig_ra_deg),  \
                     ('%.8f' % r['orig_dec_deg'] == '%.8f' % self.orig_dec_deg),  \
                     ('%.4f' % r['right_ascension'] == '%.4f' % self.right_ascension),  \
                     ('%.4f' % r['declination'] == '%.4f' % self.declination),  \
                     ('%.8f' % r['galactic_longitude'] == '%.8f' % self.galactic_longitude),  \
                     ('%.8f' % r['galactic_latitude'] == '%.8f' % self.galactic_latitude),  \
                     ('%.8f' % r['ra_deg'] == '%.8f' % self.ra_deg),  \
                     ('%.8f' % r['dec_deg'] == '%.8f' % self.dec_deg),  \
                     ('%s' % r['obsType'].lower() == '%s' % self.obstype.lower())]

            # Match is True if _all_ matches are True
            match = all(matches)
        return match


class HeaderError(pipeline_utils.PipelineError):
    """Error to throw when a header-specific problem is encountered.
    """
    pass


def get_header(fns, beamnum=None):
    """Get header.

        Inputs:
            fns: list of filenames (include paths) of data to parse.
            beamnum: ALFA beam number (an integer between 0 and 7).
                        This is only required for multiplexed WAPP data files.

        Output:
            header: The header object.
    """
    if beamnum is not None:
        if not 0 <= beamnum <= 7:
            raise HeaderError("Beam number must be between 0 and 7, inclusive!")
        try:
            header = Header(fns, beamnum=beamnum)
        except Exception:
            raise HeaderError("Couldn't create Header object for files (%s)!" % \
                                    fns) 
    else:
        try:
            header = Header(fns)
        except Exception:
            raise HeaderError("Couldn't create Header object for files (%s)!" % \
                                    fns) 
    return header


def main():
    db = database.Database('default', autocommit=False)
    try:
        header = get_header(args, options.beamnum)
        header.upload(db)
    except:
        print "Rolling back..."
        db.rollback()
        raise
    else:
        db.commit()
    finally:
        db.close()


if __name__=='__main__':
    parser = optparse.OptionParser(usage="%prog [OPTIONS] file1 [file2 ...]")
    parser.add_option('-b', '--beamnum', dest='beamnum', type='int', \
                        help="Beam number is required for mulitplexed WAPP " \
                             "data. Beam number must be between 0 and 7, " \
                             "inclusive.", \
                        default=None)
    options, args = parser.parse_args()
    main()
