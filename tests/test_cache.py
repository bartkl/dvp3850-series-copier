from dvp3850_shows_copier.cache import Cache


def test_cache():
    cache = Cache('/home/bart/dvp3850-compat-test.json', data={})
    cache.clear()
    cache.write()

    assert cache == {}

    cache.set_compatible("/media/droppie/libraries/shows/South Park/Season 01/S01E01 - Cartman gets an anal probe.avi")
    assert cache != {}
    cache.clear()
    assert cache == {}

    cache.set_compatible("/media/droppie/libraries/shows/South Park/Season 01/S01E01 - Cartman gets an anal probe.avi")
    cache.set_incompatible("South Park/Season 02/S02E02 - Cartman's mom is still a dirty slut.avi")
    
    ep = "/media/droppie/libraries/shows/South Park/Season 02/S02E03 - Chickenlover.avi"
    cache.set_compatible(ep)
    assert cache[ep] == True

    cache.write()
    
    try:
        cache.set_incompatible("Ssouth Park/Season 02/S02E02 - Cartman's mom is still a dirty slut.avi")
    except ValueError as e:
        if e.args[0] != 'Unknown show "Ssouth Park".':
            raise

if __name__ == '__main__':
    test_cache()
