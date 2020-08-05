apiVersion: core.oam.dev/v1alpha2
kind: ApplicationConfiguration
metadata:
  name: randomClassification
  annotations:
    version: v1.0.0
    description: "random classifier"
spec:
  components:
    - componentName: random-classifier
---
apiVersion: core.oam.dev/v1alpha2
kind: ContainerizedWorkload
metadata:
  name: random-classifier
  acrUsecase: breast_density
spec:
  workload:
    apiVersion: core.oam.dev/v1alpha2
    kind: Server
    spec:
      osType: linux
      containers:
      - name: random-class-container
        image: random
        cmd: docker run random --inputVolume /iv --outputVolume /ov --scratchVolume /sv --gpu 0 --reportUrl 'https://foo.bar' --jobId job0 
        resources:
          cpu:
            required: 1.0
          memory:
            required: 100MB
          gpu:
            required: 1.0
          volume:
          - name: "inputVolume"
            mountPath: /input
            accessMode: RO
            sharingPolicy: Shared
          - name: "ouputVolume"
            mountPath: /output
            accessMode: RW
            sharingPolicy: Shared
          - name: "scratchVolume"
            mountPath: /scratch
            accessMode: RW
            sharingPolicy: Shared
        env:
          - name: "inputFiletype"
            value: "DICOM"
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