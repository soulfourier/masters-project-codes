import PySpin 
import matplotlib.pyplot as plt
import numpy as np
import keyboard
import sys

global continue_recording
continue_recording = True

def close_acquisition(evt):
    global continue_recording
    continue_recording = False

def exposure_control(cam):
    try:
        result = True
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print("unable to disable auto exposure...Abort")
            result = False
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            print("unable to disable auto exposure...Abort")
            result = False

        exposure_time = 12000 #in microseconds
        print("Maximum exposure time", cam.ExposureTime.GetMax(),"\n exposure time is set to %s us" % exposure_time)
        exposure_time = min(cam.ExposureTime.GetMax(), exposure_time)
        cam.ExposureTime.SetValue(exposure_time)

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def reset_exp(cam):
    try:
        result = True
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print("unable to enable auto exposure")
            result = False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result    

def acquire_display(cam, nodemap, nodemap_tldevice):
    global continue_recording
    stream_nodemap = cam.GetTLStreamNodeMap()
    buffer_handle_mode = PySpin.CEnumerationPtr(stream_nodemap.GetNode('StreamBufferHandlingMode'))
    if not PySpin.IsReadable(buffer_handle_mode) or not PySpin.IsWritable(buffer_handle_mode):
        print("Unable to stream buffer handling mode")
        return False
    new_only_mode = buffer_handle_mode.GetEntryByName("NewestOnly")
    if not PySpin.IsReadable(new_only_mode):
        print("Unable to Stream")
        return False
    new_only_mode = new_only_mode.GetValue()
    print(type(new_only_mode))
    buffer_handle_mode = buffer_handle_mode.SetIntValue(new_only_mode)


    print('Acquiring Images\n')
    try:
        if cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
            print('Unable to set acquisition mode to continuous. Aborting...')
            return False

        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        print('Acquisition mode set to continuous...')
        

        print('Acquisition mode is set to continuous...')

        cam.BeginAcquisition()

        print('Acquiring images...')

        serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsReadable(node_device_serial_number):
            serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % serial_number)

        print('Press enter to close the program..')
        # The next part of the code is written to set a value for GetNextImage delay for acquiring image from buffer
        timeout = 0
        if cam.ExposureTime.GetAccessMode() == PySpin.RW or cam.ExposureTime.GetAccessMode() == PySpin.RO:
            
            timeout = (int)(cam.ExposureTime.GetValue() / 1000 + 1000)
        else:
            print ('Unable to get exposure time. Aborting...')
            return False
        
        processor = PySpin.ImageProcessor()
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
       

        fig = plt.figure(1)

        fig.canvas.mpl_connect('close_event', close_acquisition)

        while(continue_recording):
            try: 
                image_result = cam.GetNextImage(timeout)
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                    
                else:
                    image_data = image_result.GetNDArray()
                    
                    plt.imshow(image_data, cmap='gray')
                    plt.pause(0.001)
                    plt.clf()
                    if keyboard.is_pressed('TAB'):
                        image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
                        print(image_converted)
                        filename = 'FLIR_1_from-%s.jpg' % (serial_number)
                        image_converted.Save(filename)
                    if keyboard.is_pressed('ENTER'):
                        print('Program is closed')
                        
                        plt.close('all')             
                        input('Done! Press Enter to exit...')
                        continue_recording=False 
            except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    result = False
        cam.EndAcquisition()
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False
    return True



def run_camera(cam):

    try:
        result = True
        nodemap_tldevice = cam.GetTLDeviceNodeMap()
        cam.Init()
        nodemap = cam.GetNodeMap()

        if not exposure_control(cam):
            return False
        result &= acquire_display(cam, nodemap, nodemap_tldevice)
        result &= reset_exp(cam)
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def main():
    result = True
    system = PySpin.System.GetInstance()
    version = system.GetLibraryVersion()
    cam_list = system.GetCameras()
    number_cam = np.size(cam_list)
    
    if number_cam == 0:
        cam_list.Clear()
        system.ReleaseInstance()
        print("No cameras are connected")
        return False
    
    for cam in cam_list:
        print("running camera")
        result &= run_camera(cam)
    
    del cam
    cam_list.Clear()
    system.ReleaseInstance()
    input('Done! Press Enter to exit...') 

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)