from dependency_injector import containers, providers
from app.resume_building.resume_convert import ResumeConverter


class ResumeConverterContainer(containers.DeclarativeContainer):
    # No dependencies needed as ResumeConverter is instantiated with an empty dict
    resume_converter = providers.Factory(
        ResumeConverter,
        data={}
    ) 