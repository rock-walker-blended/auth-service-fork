import factory

import factories.data.data_for_factories as data
import factories.factory_models.client_factory as cl_factory
import factories.factory_models.user_factory as user_factory
import factories.factory_session as sess


factory.random.reseed_random(0)


class DataBasePopulation:
    @classmethod
    def populate_database(cls):
        # clean data from the tables in database
        cls.clean_data_from_database()

        # populate database
        cls.populate_client_table()
        cls.populate_user_table()
        cls.populate_claims_table()
        cls.populate_client_secrets()

    @classmethod
    def clean_data_from_database(cls):
        sess.session.execute("TRUNCATE TABLE persistent_grants RESTART IDENTITY")
        sess.session.execute("TRUNCATE TABLE client_secrets RESTART IDENTITY")
        sess.session.execute("TRUNCATE TABLE user_claims RESTART IDENTITY")
        sess.session.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE ")
        sess.session.execute("TRUNCATE TABLE clients RESTART IDENTITY CASCADE ")
        sess.session.commit()

    @classmethod
    def populate_client_table(cls):

        for i in range(len(data.CLIENT_IDS)):
            client = cl_factory.ClientFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_user_table(cls):
        for i in range(len(data.CLIENT_USERNAMES)):
            user = user_factory.UserFactory()
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_claims_table(cls):
        for key, val in data.DEFAULT_USER_CLAIMS.items():
            claim = user_factory.UserClaimFactory(
                user_id=1, claim_type=key, claim_value=val
            )
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_client_secrets(cls):
        for client_id, secret in data.CLIENT_SECRETS.items():
            sec = cl_factory.ClientSecretFactory(client_id=client_id, value=secret)
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()


if __name__ == "__main__":
    DataBasePopulation.populate_database()
