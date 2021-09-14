import pandas as pd

from tods import schemas as schemas_utils
from tods import generate_dataset, evaluate_pipeline, fit_pipeline, load_fitted_pipeline_by_pipeline, load_fitted_pipeline_by_id, save, load, save2, load_pipeline, load2, testss, check_runtime_diff


from d3m.metadata import base as metadata_base
from axolotl.backend.simple import SimpleRunner
import uuid


from d3m import index
from d3m.metadata.base import ArgumentType
from d3m.metadata.pipeline import Pipeline, PrimitiveStep

# Creating pipeline
pipeline_description = Pipeline()
pipeline_description.add_input(name='inputs')

# Step 0: dataset_to_dataframe
step_0 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.data_processing.dataset_to_dataframe'))
step_0.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='inputs.0')
step_0.add_output('produce')
pipeline_description.add_step(step_0)

# Step 1: column_parser
step_1 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.data_processing.column_parser'))
step_1.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='steps.0.produce')
step_1.add_output('produce')
pipeline_description.add_step(step_1)

# Step 2: extract_columns_by_semantic_types(attributes)
step_2 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.data_processing.extract_columns_by_semantic_types'))
step_2.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='steps.1.produce')
step_2.add_output('produce')
step_2.add_hyperparameter(name='semantic_types', argument_type=ArgumentType.VALUE,
							  data=['https://metadata.datadrivendiscovery.org/types/Attribute'])
pipeline_description.add_step(step_2)

# Step 3: extract_columns_by_semantic_types(targets)
step_3 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.data_processing.extract_columns_by_semantic_types'))
step_3.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='steps.0.produce')
step_3.add_output('produce')
step_3.add_hyperparameter(name='semantic_types', argument_type=ArgumentType.VALUE,
							data=['https://metadata.datadrivendiscovery.org/types/TrueTarget'])
pipeline_description.add_step(step_3)

attributes = 'steps.2.produce'
targets = 'steps.3.produce'

# Step 4: processing
#step_4 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.timeseries_processing.transformation.axiswise_scaler'))
step_4 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.feature_analysis.statistical_maximum'))
#step_4 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.feature_analysis.statistical_minimum'))
step_4.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference=attributes)
step_4.add_output('produce')
pipeline_description.add_step(step_4)

# Step 5: algorithm`
step_5 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.detection_algorithm.pyod_ae'))
step_5.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='steps.4.produce')
step_5.add_output('produce')
pipeline_description.add_step(step_5)

# step_6 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.detection_algorithm.matrix_profile'))
# step_6.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='steps.5.produce')
# step_6.add_output('produce')
# pipeline_description.add_step(step_6)

# # Step 6: Predictions
# step_7 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.data_processing.construct_predictions'))
# step_7.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='steps.6.produce')
# step_7.add_argument(name='reference', argument_type=ArgumentType.CONTAINER, data_reference='steps.1.produce')
# step_7.add_output('produce')
# pipeline_description.add_step(step_7)


step_6 = PrimitiveStep(primitive=index.get_primitive('d3m.primitives.tods.data_processing.construct_predictions'))
step_6.add_argument(name='inputs', argument_type=ArgumentType.CONTAINER, data_reference='steps.5.produce')
step_6.add_argument(name='reference', argument_type=ArgumentType.CONTAINER, data_reference='steps.1.produce')
step_6.add_output('produce')
pipeline_description.add_step(step_6)



# Final Output
pipeline_description.add_output(name='output predictions', data_reference='steps.6.produce')

# Output to json
data = pipeline_description.to_json()
with open('autoencoder_pipeline.json', 'w') as f:
    f.write(data)
    print(data)



table_path = 'datasets/anomaly/raw_data/yahoo_sub_5.csv'
df = pd.read_csv(table_path)
dataset = generate_dataset(df, 6)
# pipeline = schemas_utils.load_default_pipeline()
pipeline = load_pipeline('autoencoder_pipeline.json')

id_, fitted_pipeline = save2(dataset, pipeline, 'F1_MACRO')

table_path = 'datasets/anomaly/raw_data/yahoo_sub_5.csv'
df = pd.read_csv(table_path)
dataset = generate_dataset(df, 5)

pipeline_result, loaded_fitted_pipeline = load2(dataset, id_)

print(pipeline_result)


check_runtime_diff(fitted_pipeline, loaded_fitted_pipeline)

# print(evaluate_pipeline(dataset, pipeline, 'F1_MACRO'))

# works:
# pyod_ae
# pyod_vae
# pyod_cof
# pyod_sod
# pyod_abod
# pyod_hbos
# pyod_iforest
# pyod_lof
# pyod_knn
# pyod_ocsvm
# pyod_loda
# pyod_cblof
# pyod_sogaal
# pyod_mogaal

# AutoRegODetector

# LSTMOutlierDetector
# PCAODetector

# KDiscordODetector
# DeeplogLstm
# matrix profile
# telemnon

# not working

