# garden-recorder
Java application and pythocn-callable jar for slicing live/long audio data, with a 3-trigger system, to a database of metadata and audio fragments. 

The standalone FieldRecorder application can be used as an autonomous recording station. The same jar file can be called to perform offline processing of a collection of audio files, for example, from an audiomoth or Frontier Labs recording devices. The python folder has code for different devices. 

The output of this processing is a collection of folders of short audio files (see conf parameters) and a metadata json file that has exact time-stamps of the recordings and information abou tthe trigger values. 

For the trigger mechanism, see the original publication and a corresponding data set [here](https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/HPLUCH). See also our [DCASE 2025 paper](https://dcase.community/documents/workshop2025/proceedings/DCASE2025Workshop_Koutsogeorgos_24.pdf) 

### Citation

If you use this code in your research, please cite:

```bibtex
@inproceedings{aki_harma_bird_2024,
	address = {Lyon, France},
	title = {Bird {Activities} in a {Residential} {Back} {Garden}},
	booktitle = {Proc. {EUSIPCO}'24},
	author = {{Aki Härmä} and {Evgeny Nazarenko}},
	month = aug,
	year = {2024},
}
```



