from src.config.config import config
from src.database.database_connection import execute_query

class TrainingService:
    
    @staticmethod
    def get_training_readiness():
        query = f"""
        SELECT 
            COUNT(DISTINCT s.user_id) as total_users,
            COUNT(DISTINCT s.session_id) as total_sessions,
            COUNT(DISTINCT ua.activity_uuid) as total_activities,
            MIN(s.created_at) as first_session,
            MAX(s.created_at) as last_session
        FROM {config.DB_SCHEMA_SESSION}.sessions s
        LEFT JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
        WHERE s.user_id NOT BETWEEN 1001 AND 1100
        """
        
        result = execute_query(query)
        
        if not result:
            return {
                'ready': False,
                'total_users': 0,
                'required_users': 50,
                'message': 'No hay datos reales disponibles'
            }
        
        stats = result[0]
        total_users = stats['total_users']
        required_users = 50
        
        return {
            'ready': total_users >= required_users,
            'total_users': total_users,
            'required_users': required_users,
            'total_sessions': stats['total_sessions'],
            'total_activities': stats['total_activities'],
            'first_session': str(stats['first_session']) if stats['first_session'] else None,
            'last_session': str(stats['last_session']) if stats['last_session'] else None,
            'message': f'Listos {total_users}/{required_users} usuarios' if total_users >= required_users else f'Faltan {required_users - total_users} usuarios'
        }
    
    @staticmethod
    def retrain_model():
        status = TrainingService.get_training_readiness()
        
        if not status['ready']:
            raise ValueError(status['message'])
        
        return {
            'status': 'pending',
            'message': 'Reentrenamiento programado. Ejecutar notebook 03_clustering_real_training.ipynb'
        }