from jl.cache import ArgumentCache


def test_cache_retention(tmp_path):
    cache = ArgumentCache(cache_dir=tmp_path)

    justfile = "/tmp/justfile"
    recipe = "deploy"
    args = {"env": "prod", "tag": "v1"}

    cache.save_arguments(justfile, recipe, args)

    assert (tmp_path / "history.json").exists()

    new_cache = ArgumentCache(cache_dir=tmp_path)
    loaded_args = new_cache.get_last_arguments(justfile, recipe)

    assert loaded_args == args


def test_cache_key_separation(tmp_path):
    cache = ArgumentCache(cache_dir=tmp_path)

    cache.save_arguments("/project1/justfile", "build", {"target": "debug"})
    cache.save_arguments("/project2/justfile", "build", {"target": "release"})

    args1 = cache.get_last_arguments("/project1/justfile", "build")
    args2 = cache.get_last_arguments("/project2/justfile", "build")

    assert args1["target"] == "debug"
    assert args2["target"] == "release"
