from pipeline.workers.create_dockers import CreateDockers


def test_create_dockers():    
    cd_worker = CreateDockers({}, {}, {})
    out = cd_worker.run()
    assert out
