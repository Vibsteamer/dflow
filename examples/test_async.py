from dflow import (
    ShellOPTemplate,
    InputArtifact,
    OutputArtifact,
    Workflow,
    Step
)
import time

if __name__ == "__main__":
    hello = ShellOPTemplate(name='Hello',
            image="alpine:latest",
            script="sleep 60 && echo Hello > /tmp/bar.txt")
    hello.outputs.artifacts = {"bar": OutputArtifact(path="/tmp/bar.txt")}

    echo = ShellOPTemplate(name='Echo',
                image="alpine:latest",
                script="while [ 1 ]; do echo 'waiting...'; if [ -f /tmp/foo.txt ]; then cat /tmp/foo.txt; break; fi; sleep 1; done")
    echo.inputs.artifacts = {"foo": InputArtifact(path="/tmp/foo.txt")}

    wf = Workflow(name="async")
    step0 = Step(name="hello", template=hello)
    # This step will give output artifact "bar" which contains "Hello" after 60 seconds
    step1 = Step(name="echo", template=echo, artifacts={"foo": step0.outputs.artifacts["bar"].pvc()})
    # This step will wait the last step to finish and then print its output artifact
    wf.add([step0, step1])
    wf.submit()

    while wf.query_status() in ["Pending", "Running"]:
        time.sleep(1)

    assert(wf.query_status() == "Succeeded")
