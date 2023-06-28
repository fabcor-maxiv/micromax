#!/usr/bin/env python

from tango.server import Device, attribute


class Eiger(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._compression = "bslz4"

    @attribute(name="NbImages", dtype=int)
    def nb_images(self):
        return 1800

    @attribute(name="Temperature", dtype=float)
    def temperature(self):
        return 24.2

    @attribute(name="Humidity", dtype=float)
    def humidity(self):
        return 80.2

    @attribute(name="CountTime", dtype=float)
    def count_time(self):
        return 32.2

    @attribute(name="FrameTime", dtype=float, min_value=0.00204081693664193)
    def frame_time(self):
        return 0.04

    @attribute(name="PhotonEnergy", dtype=float, min_value=4000, max_value=160000)
    def photon_energy(self):
        return 6000

    @attribute(name="Wavelength", dtype=float)
    def wavelength(self):
        return 0.04

    @attribute(name="EnergyThreshold", dtype=float)
    def energy_threshold(self):
        return 5000

    @attribute(name="FlatfieldEnabled", dtype=bool)
    def flatfield_enabled(self):
        return False

    @attribute(name="AutoSummationEnabled", dtype=bool)
    def auto_summation_enabled(self):
        return False

    @attribute(name="TriggerMode", dtype=str)
    def trigger_mode(self):
        return "TriggerMode TBD"

    @attribute(name="RateCorrectionEnabled", dtype=bool)
    def rate_correction_enabled(self):
        return False

    @attribute(name="BitDepth", dtype=int)
    def bit_depth(self):
        return 16

    @attribute(name="ReadoutTime", dtype=float)
    def readout_time(self):
        return 0.23

    @attribute(name="Description", dtype=str)
    def description(self):
        return "Description TBD"

    @attribute(name="Time", dtype=str)
    def time(self):
        return "Time TBD"

    @attribute(name="NbTriggers", dtype=int)
    def nb_triggers(self):
        return 3

    @attribute(name="XPixelSize", dtype=float)
    def x_pixel_size(self):
        return 0.23

    @attribute(name="YPixelSize", dtype=float)
    def y_pixel_size(self):
        return 0.23

    @attribute(name="CountTimeInte", dtype=float)
    def count_time_inte(self):
        return 0.23

    @attribute(name="DownloadDirectory", dtype=str)
    def download_directory(self):
        return "DownloadDirectory TBD"

    @attribute(name="FilesInBuffer", dtype=str)
    def files_in_buffer(self):
        return "FilesInBuffer TBD"

    @attribute(name="Error", dtype=str)
    def error(self):
        return "Error TBD"

    @attribute(name="BeamCenterX", dtype=float)
    def beam_center_x(self):
        return 0.0

    @attribute(name="BeamCenterY", dtype=float)
    def beam_center_y(self):
        return 0.0

    @attribute(name="DetectorDistance", dtype=float)
    def detector_distance(self):
        return 500

    @attribute(name="OmegaIncrement", dtype=float)
    def omega_increment(self):
        return 0.01

    @attribute(name="OmegaStart", dtype=float)
    def omega_start(self):
        return 1.1

    @attribute(name="RoiMode", dtype=str)
    def roi_mode(self):
        return "RoiMode TBD"

    @attribute(name="XPixelsDetector", dtype=int)
    def x_pixels_detector(self):
        return 2**16

    @attribute(name="YPixelsDetector", dtype=int)
    def y_pixels_detector(self):
        return 2**16

    @attribute(name="CollectionUUID", dtype=str)
    def collection_uuid(self):
        return "f12336a0-dcbe-484d-9f86-2fc4ac614846"

    @attribute(name="HeaderDetail", dtype=str)
    def header_detail(self):
        return "HeaderDetail TBD"

    @attribute(name="HeaderAppendix", dtype=str)
    def header_appendix(self):
        return "HeaderAppendix TBD"

    @attribute(name="ImageAppendix", dtype=str)
    def image_appendix(self):
        return "ImageAppendix TBD"

    @attribute(name="StreamState", dtype=str)
    def stream_state(self):
        return "StreamState TBD"

    @attribute(name="FilenamePattern", dtype=str)
    def filename_pattern(self):
        return "FilenamePattern TBD"

    @attribute(name="ImagesPerFile", dtype=int)
    def images_per_file(self):
        return 100

    # remaining buffer space in KB
    @attribute(name="BufferFree", dtype="DevULong64")
    def buffer_free(self):
        return 1024 * 1024 * 10

    # The filewriter`s status. The status can be one of disabled,
    # ready, acquire, and error.
    @attribute(name="FilewriterState", dtype=str)
    def filewriter_state(self):
        return "ready"

    # image_nr_low metadata parameter in the first HDF5 data file
    @attribute(name="ImageNbStart", dtype=int)
    def image_nb_start(self):
        return 0

    # image_nr_low metadata parameter in the first HDF5 data file
    @attribute(name="MonitorMode", dtype=str)
    def monitor_mode(self):
        return "MonitorMode TBD"

    @attribute(name="DiscardNew", dtype=bool)
    def discard_new(self):
        return False

    # Operation mode, can be enabled or disabled
    @attribute(name="FilewriterMode", dtype=str)
    def filewriter_mode(self):
        return "enabled"

    compression = attribute(name="Compression", dtype=str)

    @compression.getter
    def _compression_read(self):
        return self._compression

    @compression.setter
    def _compression_write(self, value):
        self._compression = value


if __name__ == "__main__":
    Eiger.run_server()
