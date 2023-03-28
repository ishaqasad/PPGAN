import matplotlib.pyplot as plt
import string
import mido
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)


def msg2dict(msg):
    result = dict()
    if 'note_on' in msg:
        on_ = True
    elif 'note_off' in msg:
        on_ = False
    else:
        on_ = None
    result['time'] = int(msg[msg.rfind('time'):].split(' ')[0].split('=')[1].translate(
        str.maketrans({a: None for a in string.punctuation})))

    if on_ is not None:
        for k in ['note', 'velocity']:
            result[k] = int(msg[msg.rfind(k):].split(' ')[0].split('=')[1].translate(
                str.maketrans({a: None for a in string.punctuation})))
    #print([result, on_])
    return [result, on_]

def switch_note(last_state, note, velocity, on_=True):
    # piano has 88 notes, corresponding to note id 21 to 108, any note out of this range will be ignored
    result = [0] * 88 if last_state is None else last_state.copy()
    if 21 <= note <= 108:
        result[note-21] = velocity if on_ else 0
    return result

def get_new_state(new_msg, last_state):
    new_msg, on_ = msg2dict(str(new_msg))
    new_state = switch_note(last_state, note=new_msg['note'], velocity=new_msg['velocity'], on_=on_) if on_ is not None else last_state
    return [new_state, new_msg['time']]

def track2seq(track):
    # piano has 88 notes, corresponding to note id 21 to 108, any note out of the id range will be ignored
    result = []
    last_state, last_time = get_new_state(str(track[0]), [0]*88)
    '''
    for i in range(1, len(track)):
        new_state, new_time = get_new_state(track[i], last_state)
        if new_time > 0:
            result += [last_state]*new_time
        last_state, last_time = new_state, new_time
    '''
    #print("yaya", len(track))
    for i in range(1, len(track)):
        new_state, new_time = get_new_state(track[i], last_state)
        if new_time > 0:
            result += [last_state]*new_time
        last_state, last_time = new_state, new_time
    #print("HIHIHIHIHIHI", result)
    return result

def mid2arry(mid, min_msg_pct=0.1):
    print(len(mid.tracks))
    #print(mid.tracks[0])
    tracks_len = [len(tr) for tr in mid.tracks] #creates list that contains length of each track in mid object
    print(tracks_len)
    min_n_msg = max(tracks_len) * min_msg_pct
    # convert each track to nested list
    piano = []
    vocal = []
    #print(mid.tracks[1])

    #piano
    for i in range(1, len(mid.tracks)):
        if len(mid.tracks[i]) > min_n_msg:
            ary_i = track2seq(mid.tracks[i])
            piano.append(ary_i)

    #vocal
    if len(mid.tracks[0]) > min_n_msg:
        ary_i = track2seq(mid.tracks[0])
        vocal.append(ary_i)

    # make all nested list the same length
    max_piano = max([len(ary) for ary in piano])
    max_vocal = max([len(ary) for ary in vocal])
    max_len = max(max_piano, max_vocal)
    for i in range(len(piano)):
        if len(piano[i]) < max_len:
            piano[i] += [[0] * 88] * (max_len - len(piano[i]))

    #max_len = max([len(ary) for ary in vocal])
    for i in range(len(vocal)):
        if len(vocal[i]) < max_len:
            vocal[i] += [[0] * 88] * (max_len - len(vocal[i]))
    #print("not np", all_arys)

    piano = np.array(piano)
    vocal = np.array(vocal)

    #print(all_arys)
    piano = piano.max(axis=0)
    vocal = vocal.max(axis=0)
    # trim: remove consecutive 0s in the beginning and at the end
    #sums = piano.sum(axis=1)
    #ends = np.where(sums > 0)[0]

    #sums_v = vocal.sum(axis=1)
    #ends_v = np.where(sums_v > 0)[0]

    #return vocal[min(ends_v): max(ends_v)], piano[min(ends): max(ends)]
    return vocal, piano

    #return all_arys

def shrink_matrix(matrix):
    new_matrix = np.empty((0, matrix.shape[1]), matrix.dtype)
    for i, row in enumerate(matrix):
        # Check if the current row index is divisible by 120
        if i % 120 == 0:
            # If it is, append the row to the new matrix
            new_matrix = np.vstack((new_matrix, row))
    return new_matrix

def save_matrix(matrix, path):
    num_rows_per_file = 64
    num_files = int(np.ceil(matrix.shape[0] / num_rows_per_file))
    print("num_files is", num_files)
    for i in range(num_files):
        start_row = i * num_rows_per_file
        end_row = (i + 1) * num_rows_per_file
        chunk = matrix[start_row:end_row]

        if chunk.shape[0] < num_rows_per_file:
            # If the chunk has less than 64 rows, pad it with zeros
            num_rows_to_pad = num_rows_per_file - chunk.shape[0]
            padding = np.zeros((num_rows_to_pad, matrix.shape[1]), matrix.dtype)
            chunk = np.vstack((chunk, padding))

        print(len(chunk))
        print(i)
        #print(chunk)
        file_name = path + "_" + str(i)
        np.save(file_name, chunk)


if __name__ == '__main__':
    midi_file_path = "some.mid"
    mid = mido.MidiFile(midi_file_path, clip=True)
    print(mid.ticks_per_beat)
    vocal, piano = mid2arry(mid)

    #print(result_array[:10])
    print(np.shape(vocal), np.shape(piano))
    final_vocal = shrink_matrix(vocal)
    final_piano = shrink_matrix(piano)
    print(np.shape(final_vocal), np.shape(final_piano))
    #print(final_piano)
    #print(np.shape(final))
    path_vocal = "inputs\\" + midi_file_path
    path_piano = "outputs\\" + midi_file_path
    #print(path)
    save_matrix(final_vocal, path_vocal)
    save_matrix(final_piano, path_piano)

    #plt.plot(range(result_array.shape[0]), np.multiply(np.where(result_array>0, 1, 0), range(1, 89)), marker='.', markersize=1, linestyle='')
    plt.title("midi plot")
    #plt.show()