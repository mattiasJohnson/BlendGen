# BlendGen
Generate image data from blender models.

## Install

```
git clone https://github.com/mattiasJohnson/BlendGen.git
```

```
cd BlendGen
```

```
python -m pip install --editable .
```


## How to run

Example:
```
blendgen
```

With flags:
```
blendgen --prop-path=. --save-path=. --save-name=test_name --n-images=1 --n-instances=1
```


## Example renders
![Rendered image](example_render.png)
![Segmentation of image](example_render_seg.png)