apiVersion: core.oam.dev/v1alpha2
kind: ApplicationConfiguration
metadata:
  name: my-pneumonia-build
  annotations:
    version: v1.0.0
    description: "Docker for pneumonia detection"
spec:
  components:
    - componentName: example-aimodel-server
      parameterValues:
        - name: buildArg1
          value: "Well hello there"
        - name: buildArg2
          value: "www.example.com"
---
apiVersion: core.oam.dev/v1alpha2
kind: ContainerizedWorkload
metadata:
  name: example-aimodel-server
  acrUsecase: example-use-case
  rde_339Threshold: 0.3
spec:
  workload:
    apiVersion: core.oam.dev/v1alpha2
    kind: Server
    spec:
      osType: linux
      containers:
      - name: my-aimodel-server
        image: example/my-aimodel-server@sha256:72e996751fe42b2a0c1e6355730dc2751ccda50564fec929f76804a6365ef5ef
        cmd: docker run my-aimodel-server --inputVolume /iv --outputVolume /ov --scratchVolume /sv python main.py --gpu 0 --reportUrl 'https://foo.bar' --jobId job0 --modelFilepath model.pt
        resources:
          cpu:
            required: 1.0
          memory:
            required: 100MB
          gpu:
            required: 1.0
          volume:
          - name: "inputVolume"
            mountPath: /usr/input
            accessMode: RO
            sharingPolicy: Shared
          - name: "ouputVolume"
            mountPath: /usr/output
            accessMode: RW
            sharingPolicy: Shared
          - name: "scratchVolume"
            mountPath: /usr/scratch
            accessMode: RW
            sharingPolicy: Shared
        env:
          - name: "inputFiletype"
            value: "DICOM"
        ports:
        - name: http
          value: 8080
        parameters:
          - name: "gpu"
            type: number
            defaultValue: 0
          - name: "reportUrl"
            type: string
            defaultValue: “http://foo.bar”
            required: TRUE
          - name: "jobId"
            type: string
            defaultValue: “job0”
            required: TRUE
          - name: "modelFilepath"
            type: string
            defaultValue: “model.pt”
