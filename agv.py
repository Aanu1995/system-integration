from opcua import Client, ua
import time


# -----------------------------------------------------------
# CLASS TO HOLD NODE VALUES
# -----------------------------------------------------------
class AGVState:
    def __init__(self):
        self.ixAGVAtHome = False
        self.ixAGVAtCrane = False
        self.ixAGVAtUR = False
        self.qxMoveAGVToHome = False
        self.qxMoveAGVToCrane = False
        self.qxMoveAGVToUR = False
        self.qxOrder = -1
        self.qxStatus = 0
        self.qxSetupStatus = 0
        self.requestReceived = False



# -----------------------------------------------------------
# SUBSCRIPTION HANDLER
# -----------------------------------------------------------
class SubHandler:
    def __init__(self, state, node_ids):
        self.state = state
        self.node_ids = node_ids  # dictionary of node ID strings

    def datachange_notification(self, node, val, data):
        node_id = node.nodeid.to_string()

        if node_id == self.node_ids["ixAGVAtHome"]:
            self.state.ixAGVAtHome = val

        if node_id == self.node_ids["ixAGVAtCrane"]:
            self.state.ixAGVAtCrane = val

        if node_id == self.node_ids["ixAGVAtUR"]:
            self.state.ixAGVAtUR = val

        if node_id == self.node_ids["qxMoveAGVToHome"]:
            self.state.qxMoveAGVToHome = val

        if node_id == self.node_ids["qxMoveAGVToCrane"]:
            self.state.qxMoveAGVToCrane = val

        if node_id == self.node_ids["qxMoveAGVToUR"]:
            self.state.qxMoveAGVToUR = val

        if node_id == self.node_ids["qxOrder"]:
            self.state.qxOrder = val

        if node_id == self.node_ids["qxStatus"]:
            self.state.qxStatus = val
        
        if node_id == self.node_ids["qxSetupStatus"]:
            self.state.qxSetupStatus = val

        if node_id == self.node_ids["requestReceived"]:
            self.state.requestReceived = val


def main():

    # -----------------------------------------------------------
    # NODE IDS
    # -----------------------------------------------------------
    node_ids = {
        "ixAGVAtHome":        "ns=4;s=GVL.ixAGVAtHome",
        "ixAGVAtCrane":        "ns=4;s=GVL.ixAGVAtCrane",
        "ixAGVAtUR":           "ns=4;s=GVL.ixAGVAtUR",
        "qxMoveAGVToHome":     "ns=4;s=GVL.qxMoveAGVToHome",
        "qxMoveAGVToCrane":    "ns=4;s=GVL.qxMoveAGVToCrane",
        "qxMoveAGVToUR":       "ns=4;s=GVL.qxMoveAGVToUR",
        "qxOrder":             "ns=4;s=GVL.qxOrder",
        "qxStatus":            "ns=4;s=GVL.qxStatus",
        "qxSetupStatus":       "ns=4;s=GVL.qxSetupStatus",
        "requestReceived":     "ns=4;s=GVL.requestReceived",
    }

    # -----------------------------------------------------------
    # AGV STATE OBJECT (NO GLOBALS)
    # -----------------------------------------------------------
    state = AGVState()



    # -----------------------------------------------------------
    # CONNECT
    # -----------------------------------------------------------
    url = "opc.tcp://169.254.70.51:4840"
    client = Client(url)
    client.set_user("Admin")
    client.set_password("1")
    client.set_security_string("Basic256Sha256,SignAndEncrypt,Beckhoff_OpcUaServer.der,Beckhoff_OpcUaServer.pem")

    sub = None          # will hold the subscription object
    handles = []        # will hold monitored item handles

    try:
        print("Connecting...")
        client.connect()
        print("Connected.")

        # -----------------------------------------------------------
        # CREATE NODE OBJECTS
        # -----------------------------------------------------------
        n_ixAGVAtHome = client.get_node(node_ids["ixAGVAtHome"])
        n_ixAGVAtCrane = client.get_node(node_ids["ixAGVAtCrane"])
        n_ixAGVAtUR = client.get_node(node_ids["ixAGVAtUR"])
        n_qxMoveAGVToHome = client.get_node(node_ids["qxMoveAGVToHome"])
        n_qxMoveAGVToCrane = client.get_node(node_ids["qxMoveAGVToCrane"])
        n_qxMoveAGVToUR = client.get_node(node_ids["qxMoveAGVToUR"])
        n_qxOrder = client.get_node(node_ids["qxOrder"])
        n_qxStatus = client.get_node(node_ids["qxStatus"])
        n_qxSetupStatus = client.get_node(node_ids["qxSetupStatus"])
        n_requestReceived = client.get_node(node_ids["requestReceived"])

        # -----------------------------------------------------------
        # INITIAL READ (updates the instance variables)
        # -----------------------------------------------------------
        state.ixAGVAtHome = n_ixAGVAtHome.get_value()
        state.ixAGVAtCrane = n_ixAGVAtCrane.get_value()
        state.ixAGVAtUR = n_ixAGVAtUR.get_value()
        state.qxMoveAGVToHome = n_qxMoveAGVToHome.get_value()
        state.qxMoveAGVToCrane = n_qxMoveAGVToCrane.get_value()
        state.qxMoveAGVToUR = n_qxMoveAGVToUR.get_value()
        state.qxOrder = n_qxOrder.get_value()
        state.qxStatus = n_qxStatus.get_value()
        state.qxSetupStatus = n_qxSetupStatus.get_value()
        state.requestReceived = n_requestReceived.get_value()

        # -----------------------------------------------------------

        print("\nInitial Values:")
        print(" ixAGVAtHome:", state.ixAGVAtHome)
        print(" ixAGVAtCrane:", state.ixAGVAtCrane)
        print(" ixAGVAtUR:", state.ixAGVAtUR)
        print(" qxMoveAGVToHome:", state.qxMoveAGVToHome)
        print(" qxMoveAGVToCrane:", state.qxMoveAGVToCrane)
        print(" qxMoveAGVToUR:", state.qxMoveAGVToUR)
        print(" qxOrder:", state.qxOrder)
        print(" qxStatus:", state.qxStatus)
        print(" qxSetupStatus:", state.qxSetupStatus)
        print(" requestReceived:", state.requestReceived)

        # -----------------------------------------------------------
        # SUBSCRIPTION
        # -----------------------------------------------------------
        handler = SubHandler(state, node_ids)
        sub = client.create_subscription(200, handler)

        handles.append(sub.subscribe_data_change(n_ixAGVAtHome))
        handles.append(sub.subscribe_data_change(n_ixAGVAtCrane))
        handles.append(sub.subscribe_data_change(n_ixAGVAtUR))
        handles.append(sub.subscribe_data_change(n_qxMoveAGVToHome))
        handles.append(sub.subscribe_data_change(n_qxMoveAGVToCrane))
        handles.append(sub.subscribe_data_change(n_qxMoveAGVToUR))
        handles.append(sub.subscribe_data_change(n_qxOrder))
        handles.append(sub.subscribe_data_change(n_qxStatus))
        handles.append(sub.subscribe_data_change(n_qxSetupStatus))
        handles.append(sub.subscribe_data_change(n_requestReceived))

        print("Listening for changes...\n")

        # -----------------------------------------------------------
        # MAIN LOOP — USE INSTANCE VARIABLES ONLY
        # -----------------------------------------------------------
        while True:
            print(
                f"[LOOP] ixAGVAtHome={state.ixAGVAtHome}, "
                f"ixAGVAtCrane={state.ixAGVAtCrane}, "
                f"ixAGVAtUR={state.ixAGVAtUR}, "
                f"qxMoveAGVToHome={state.qxMoveAGVToHome}, "
                f"qxMoveAGVToCrane={state.qxMoveAGVToCrane}, "
                f"qxMoveAGVToUR={state.qxMoveAGVToUR}, "
                f"qxOrder={state.qxOrder}, "
                f"qxStatus={state.qxStatus}, "
                f"qxSetupStatus={state.qxSetupStatus}, "
                f"requestReceived={state.requestReceived}"
            )

            # ----------------------------------------------------
            # WRITING TO PLCS
            # ----------------------------------------------------

            if state.qxStatus == 5: # setting up all systems in preparation for operation
                # Upon receiving a request to move AGV to Crane Robot, send handshake
                if state.qxMoveAGVToHome and state.requestReceived == False and state.qxSetupStatus == 1500:
                    print("-> Request Received: Move AGV to Home position")
                    n_requestReceived.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                elif state.qxMoveAGVToHome == False and state.requestReceived == False and state.qxSetupStatus == 1500:
                    print("-> moving AGV to Home Now")

                    #---------------------------------------------------------
                    # Your logic to move AGV to Home would go here
                    #---------------------------------------------------------

                    # Send command to inform PLC that AGV has arrived at Crane
                    print("-> ixAGVAtHome: True")
                    n_ixAGVAtHome.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                elif state.ixAGVAtHome and state.requestReceived and state.qxSetupStatus == 1600:
                    # Upon receiving handshake back from PLC, reset requestReceived
                    print("-> AGV has arrived at Home. Resetting requestReceived.")
                    n_ixAGVAtHome.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                    n_requestReceived.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))

            else: # Operation started

                # Upon receiving a request to move AGV to Crane Robot, send handshake
                if state.qxMoveAGVToCrane and state.requestReceived == False and state.qxStatus == 60:
                    print("-> Request Received: Move AGV from UR to Crane")
                    n_requestReceived.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                elif state.qxMoveAGVToCrane == False and state.requestReceived == False and state.qxStatus == 60:
                    print("-> moving AGV to Crane Now")

                    #---------------------------------------------------------
                    # Your logic to move AGV to Crane would go here
                    #---------------------------------------------------------

                    # Send command to inform PLC that AGV has arrived at Crane
                    print("-> ixAGVAtCrane: True")
                    n_ixAGVAtCrane.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                elif state.ixAGVAtCrane and state.requestReceived and state.qxStatus == 70:
                    # Upon receiving handshake back from PLC, reset requestReceived
                    print("-> AGV has arrived at Crane. Resetting requestReceived.")
                    n_ixAGVAtCrane.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                    n_requestReceived.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))

                # Upon receiving a request to move AGV to UR, send handshake
                elif state.qxMoveAGVToUR and state.requestReceived == False and state.qxStatus == 120:
                    print("-> Request Received: Move AGV from Crane to UR")
                    n_requestReceived.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                elif state.qxMoveAGVToUR == False and state.requestReceived == False and state.qxStatus == 120:
                    print("-> moving AGV to UR Now")

                    #---------------------------------------------------------
                    # Your logic to move AGV to UR would go here
                    #---------------------------------------------------------

                    # Send command to inform PLC that AGV has arrived at UR
                    print("-> ixAGVAtUR: True")
                    n_ixAGVAtUR.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                elif state.ixAGVAtUR and state.requestReceived and state.qxStatus == 130:
                    # Upon receiving handshake back from PLC, reset requestReceived
                    print("-> AGV has arrived at UR. Resetting requestReceived.")
                    n_ixAGVAtUR.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                    n_requestReceived.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))


            time.sleep(0.5)

    except Exception as e:
        print("Error:", e)

    finally:
        print("Cleaning up subscription...")
        try:
            if sub is not None:
                for h in handles:
                    sub.unsubscribe(h)
                sub.delete()
        except Exception as e:
            print("Error during unsubscribe/delete:", e)

        print("Disconnecting client...")
        client.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
