from os.path import isfile, isdir, exists

def assert_is_file(path):
    assert exists(path), "%s does not exist"
    assert isfile(path), "%s exists but is not a directory."

def assert_is_dir(path):
    assert exists(path), "%s does not exist"
    assert isdir(path), "%s exists but is not a directory."
