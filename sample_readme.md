apiVersion: core.oam.dev/v1alpha1
kind: ApplicationConfiguration
metadata:
  name: my-pneumonia-build
  annotations:
    version: v1.0.0
    description: "Docker for pneumonia detection"
spec:
  variables:
    - name: buildArg1
      value: "Well hello there"
    - name: buildArg2
      value: "www.example.com"
---
apiVersion: core.oam.dev/v1alpha2
kind: Component
metadata:
  name: example-aimodel-server
spec:
  workload:
    apiVersion: core.oam.dev/v1alpha2
    kind: Server
    spec:
      osType: linux
      containers:
      - name: my-aimodel-server
        image: example/my-aimodel-server@sha256:72e996751fe42b2a0c1e6355730dc2751ccda50564fec929f76804a6365ef5ef
        cmd: docker run my-aimodel-server python main.py --inputVolume /iv --outputVolume /ov --scratchVolume /sv --gpu 0 --reportUrl 'https://foo.bar' --jobId job0 --modelFilepath model.pt
        resources:
          cpu:
            required: 1.0
          memory:
            required: 100MB
          gpu:
            required: 1.0
          volume:
          - name: "inputVolume"
            mountPath: run argument
            accessMode: RO
            sharingPolicy: Shared
          - name: "ouputVolume"
            mountPath: run argument
            accessMode: RW
            sharingPolicy: Shared
          - name: "scratchVolume"
            mountPath: run argument
            accessMode: RW
            sharingPolicy: Shared
        env:
          - name: "inputFiletype"
            value: "DICOM"
        ports:
        - name: http
          value: 8080
        livenessProbe:
          httpGet:
            port: 8080
            path: /healthz
        readinessProbe:
          httpGet:
            port: 8080
            path: /healthz
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
