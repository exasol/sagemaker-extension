import pytest


def graceful_cleanup(f):
    def _inner(a):
        print("aaa")

        try:
            return f(a)
        except AssertionError as e:
            print("assert error %s" %a)
            raise pytest.fail(str(e))
        except Exception as e:
            print("exception %s" %a)
            raise pytest.fail(str(e))
        finally:
            print("finally %s" %a)
            # raise pytest.fail(e)

    return _inner

@pytest.fixture
def wtf():
    print("in fixture")
    yield
    print("delete everthing")



def test_test(wtf):
    run_test(a=10)


@graceful_cleanup
def run_test(a):
    assert a == a
    b = a / 0
