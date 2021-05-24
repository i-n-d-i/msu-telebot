import numpy as np
import sys          #argv
from scipy.io.wavfile import read, write


def print_with_timeline(data, single_duration, units_name, row_limit):
    for i in range(len(data)):
        if i % row_limit == 0:
            print(f"{single_duration * i:8.3f} {units_name} |  ", end='')
        print(f"{data[i]:.3f} ", end='')
        if (i + 1) % row_limit == 0 or i + 1 == len(data):
            print(f" | {single_duration * (i + 1):8.3f} {units_name}")



def get_segment_energy(data, start, end):
    energy = 0
    for i in range(start, end):
        energy += float(data[i]) * data[i] / (end - start)
    energy = np.sqrt(energy) / 32768
    return energy

def get_segments_energy(data, segment_duration):
    segments_energy  = []
    for segment_start in range(0, len(data), segment_duration):
        segment_stop = min(segment_start + segment_duration, len(data))
        energy = get_segment_energy(data, segment_start, segment_stop)
        segments_energy.append(energy)
    return segments_energy


def get_vad_mask(data, threshold):
    vad_mask = np.zeros_like(data)
    for i in range(0, len(data)):
        vad_mask[i] = data[i] > threshold
    return vad_mask


def sec2samples(seconds, sample_rate):
  return int(seconds * sample_rate)


class Segment:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop


def print_segments(segments, single_duration, units_name):
    total_duration = 0.0
    min_duration = 0.0
    max_duration = 0.0
    for i in range(len(segments)):
        start_units = segments[i].start * single_duration
        stop_units = segments[i].stop * single_duration
        duration_units = stop_units - start_units
        total_duration += duration_units
        if i == 0 or min_duration > duration_units:
            min_duration = duration_units
        if i == 0 or max_duration < duration_units:
            max_duration = duration_units
        print(f"{i:5}: {start_units:6.3f} - {stop_units:6.3f} ({duration_units:6.3f} {units_name})")
    print(f"Min   duration: {min_duration:.3f} {units_name}")
    print(f"Mean  duration: {total_duration / len(segments):.3f} {units_name}")
    print(f"Max   duration: {max_duration:.3f} {units_name}")
    print(f"Total segments: {len(segments)}")
    print(f"Total duration: {total_duration:.3f} {units_name}")


def mask_compress(data):
    segments = [];
    if len(data) == 0:
        return segments
    start = -1
    stop = -1
    if data[0] == 1:
        start = 0
    for i in range(len(data) - 1):
        if data[i] == 0 and data[i + 1] == 1:
            start = i + 1;
        if data[i] == 1 and data[i + 1] == 0:
            stop = i + 1;
            segments.append(Segment(start, stop));
    if data[-1] == 1:
        stop = len(data)
        segments.append(Segment(start, stop));
    return segments

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 5:
        print("Incorrect args. Example:")
        print("python3 split_by_vad.py dataset/wav/1_2_3_4_5.wav 0.1 0.01 dataset/splitted/")
        exit(1)

    wav_file_path = sys.argv[1]
    segment_duration = float(sys.argv[2])
    vad_threshold = float(sys.argv[3])
    output_wav_directory = sys.argv[4]
    
    sample_rate, audio = read(wav_file_path)

    segment_duration_samples = sec2samples(segment_duration, sample_rate)
    segments_energy = get_segments_energy(audio, segment_duration_samples)
    vad_mask = get_vad_mask(segments_energy, vad_threshold)
    segments = mask_compress(vad_mask)

    print_with_timeline(segments_energy, segment_duration, "sec", 10)
    print_with_timeline(vad_mask, segment_duration, "sec", 10)
    print_segments(segments, segment_duration, "sec")

    fname = wav_file_path[-13:-4]
    digits = fname.split("_")
    print(digits)
    assert len(digits) == len(segments), "Bad threshold"

    max_duration = 0
    for segment in segments:
        duration = (segment.stop - segment.start) * segment_duration_samples / sample_rate
        if duration > max_duration:
            max_duration = duration
    print(max_duration)
    assert max_duration <= 0.6, f"max_duration={max_duration:.3f}"

    position = 0
    for digit, segment in zip(digits, segments):
        new_wav_file_path = f"{output_wav_directory}{digit}/{fname}#{position}.wav"

        start = segment.start * segment_duration_samples
        stop = segment.stop * segment_duration_samples
        print(new_wav_file_path, start, stop)
        write(new_wav_file_path, sample_rate, audio[start:stop])

        position += 1
